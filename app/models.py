from djongo import models
from django.core.validators import RegexValidator

# --- Validadores ---
validador_solo_letras = RegexValidator(r"^[a-zA-ZÁÉÍÓÚáéíóúñÑ\s]+$", "Solo letras.")
validador_cedula = RegexValidator(r"^\d{10}$", "10 dígitos.")
validador_telefono = RegexValidator(r"^\d{7,15}$", "Teléfono válido.")

# --- Sub-modelos ---


class Representante(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    nombre = models.CharField(
        max_length=100, validators=[validador_solo_letras], null=True, blank=True
    )
    telefono = models.CharField(
        max_length=15, validators=[validador_telefono], null=True, blank=True
    )
    email = models.EmailField(max_length=100, blank=True, null=True)

    objects = models.DjongoManager()


class DatosBautismo(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    fecha = models.DateField()
    lugar = models.CharField(max_length=100)

    objects = models.DjongoManager()


class Traslado(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    fecha = models.DateField()
    origen_ref_id = models.CharField(max_length=50)
    motivo = models.CharField(max_length=200, blank=True, null=True)
    ESTADOS = [
        ("Pendiente", "Pendiente"),
        ("Aprobado", "Aprobado"),
        ("Rechazado", "Rechazado"),
    ]
    estado = models.CharField(max_length=20, choices=ESTADOS)

    objects = models.DjongoManager()


# --- Modelo Principal ---


class Catequizado(models.Model):
    _id = models.ObjectIdField(primary_key=True)

    identificacion = models.CharField(
        max_length=10, unique=True, validators=[validador_cedula]
    )
    nombres = models.CharField(max_length=100, validators=[validador_solo_letras])
    apellidos = models.CharField(max_length=100, validators=[validador_solo_letras])
    fecha_nacimiento = models.DateField(null=True)
    parroquia_actual_ref_id = models.CharField(max_length=50)

    representante = models.EmbeddedField(model_container=Representante)
    datos_bautismo = models.EmbeddedField(model_container=DatosBautismo)
    historial_traslados = models.ArrayField(model_container=Traslado, blank=True)

    def __str__(self):
        return f"{self.identificacion} - {self.nombres} {self.apellidos}"

    # --- LA MAGIA: ESTE MÉTODO ARREGLA EL ERROR DEL FORMULARIO ---
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 1. Si 'representante' llegó como diccionario, lo convertimos a Objeto
        if self.representante and isinstance(self.representante, dict):
            # Filtramos campos desconocidos para evitar errores
            valid_keys = {f.name for f in Representante._meta.get_fields()}
            clean_data = {
                k: v for k, v in self.representante.items() if k in valid_keys
            }
            self.representante = Representante(**clean_data)

        # 2. Lo mismo para 'datos_bautismo'
        if self.datos_bautismo and isinstance(self.datos_bautismo, dict):
            valid_keys = {f.name for f in DatosBautismo._meta.get_fields()}
            clean_data = {
                k: v for k, v in self.datos_bautismo.items() if k in valid_keys
            }
            self.datos_bautismo = DatosBautismo(**clean_data)

        # 3. Y para la lista de traslados
        if self.historial_traslados:
            new_list = []
            for item in self.historial_traslados:
                if isinstance(item, dict):
                    valid_keys = {f.name for f in Traslado._meta.get_fields()}
                    clean_data = {k: v for k, v in item.items() if k in valid_keys}
                    new_list.append(Traslado(**clean_data))
                else:
                    new_list.append(item)
            self.historial_traslados = new_list

    class Meta:
        verbose_name = "Catequizado"
        verbose_name_plural = "Catequizados"
        db_table = "catequizados"
