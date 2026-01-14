from djongo.models import fields
from django import forms
from django.db import models
from django.utils.safestring import mark_safe
from django.contrib.admin.widgets import AdminDateWidget
from bson import ObjectId
import datetime


# ==============================================================================
# 1. HERRAMIENTAS DE LIMPIEZA
# ==============================================================================
def clean_value_for_mongo(val):
    if isinstance(val, datetime.date) and not isinstance(val, datetime.datetime):
        return datetime.datetime.combine(val, datetime.time.min)
    if isinstance(val, str) and len(val) == 24:
        try:
            return ObjectId(val)
        except:
            pass
    return val


def clean_dict_values(data):
    new_data = {}
    for k, v in data.items():
        if isinstance(v, dict):
            new_data[k] = clean_dict_values(v)
        elif isinstance(v, list):
            new_data[k] = [clean_value_for_mongo(x) for x in v]
        else:
            new_data[k] = clean_value_for_mongo(v)
    return new_data


# ==============================================================================
# 2. AUXILIAR: MODEL TO DICT
# ==============================================================================
def model_to_dict_clean(instance):
    opts = instance._meta
    data = {}
    for field in opts.fields:
        val = getattr(instance, field.attname)
        # FIX UPDATE: No llamar a get_prep_value en campos anidados
        is_nested = isinstance(field, (fields.EmbeddedField, fields.ArrayField))
        if hasattr(field, "get_prep_value") and not is_nested:
            try:
                val = field.get_prep_value(val)
            except:
                pass
        data[field.attname] = clean_value_for_mongo(val)
    return data


# ==============================================================================
# 3. SERIALIZADOR UNIVERSAL
# ==============================================================================
def universal_serializer(self, value, connection=None, prepared=False):
    if value is None:
        if isinstance(self, fields.ArrayField):
            return []
        return None

    # ArrayField
    if isinstance(self, fields.ArrayField):
        if not isinstance(value, list):
            value = [value]
        clean_list = []
        for v in value:
            data = v
            if hasattr(v, "_meta"):
                data = model_to_dict_clean(v)
            elif isinstance(v, dict):
                data = clean_dict_values(v)

            # Filtro Anti-Fantasmas
            if isinstance(data, dict):
                if not data.get("fecha") and not data.get("origen_ref_id"):
                    continue
            clean_list.append(data)
        return clean_list

    # EmbeddedField
    if hasattr(value, "_meta"):
        return model_to_dict_clean(value)
    if isinstance(value, dict):
        return clean_dict_values(value)

    return clean_value_for_mongo(value)


# ==============================================================================
# 4. LECTURA Y UI
# ==============================================================================
def patched_to_python_general(self, value):
    if isinstance(value, datetime.datetime) and isinstance(self, models.DateField):
        return value.date()
    if value is None:
        return None
    if isinstance(value, self.model_container):
        return value
    if isinstance(value, list) and self.base_type == dict:
        return None
    return fields.MongoField.to_python(self, value)


def patched_to_python_array(self, value):
    if value is None:
        return []
    if hasattr(value, "_meta"):
        return [value]
    if isinstance(value, dict):
        return [value]
    if isinstance(value, list):
        return value
    return []


def patched_boundfield_str(self):
    instance = self.value()
    if isinstance(instance, list):
        instance = None
    model_form = self.field.model_form_class(
        instance=instance, **self.field.model_form_kwargs
    )
    for f in model_form.fields.values():
        if isinstance(f, forms.DateField):
            f.widget = AdminDateWidget()
    return mark_safe(f"<table>\n{ model_form.as_table() }\n</table>")


def patched_value_from_object(self, obj):
    return getattr(obj, self.attname)


# ==============================================================================
# 5. APLICACIÓN
# ==============================================================================
def apply_patch():
    # EmbeddedField
    fields.EmbeddedField.get_prep_value = universal_serializer
    fields.EmbeddedField.get_db_prep_value = universal_serializer
    fields.EmbeddedField.get_db_prep_save = universal_serializer
    fields.EmbeddedField.to_python = patched_to_python_general
    fields.EmbeddedField.validate = lambda self, v, m: None
    fields.EmbeddedField.value_from_object = patched_value_from_object

    # ArrayField
    fields.ArrayField.get_prep_value = universal_serializer
    fields.ArrayField.get_db_prep_value = universal_serializer
    fields.ArrayField.get_db_prep_save = universal_serializer
    fields.ArrayField.to_python = patched_to_python_array
    fields.ArrayField.validate = lambda self, v, m: None

    # --- ¡ESTA ES LA LÍNEA QUE FALTABA! ---
    # Sin esto, ArrayField usa el lector original roto.
    fields.ArrayField.value_from_object = patched_value_from_object
    # --------------------------------------

    # ModelField Base (Por seguridad)
    fields.ModelField.value_from_object = patched_value_from_object

    # Visualización
    fields.EmbeddedFormBoundField.__str__ = patched_boundfield_str

    # CharField ID Fix
    models.CharField.get_db_prep_value = (
        lambda self, value, connection, prepared=False: clean_value_for_mongo(value)
    )
