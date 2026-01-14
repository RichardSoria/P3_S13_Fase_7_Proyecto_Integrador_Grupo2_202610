from django.contrib import admin
from .models import Catequizado


@admin.register(Catequizado)
class CatequizadoAdmin(admin.ModelAdmin):
    # --- Visualización ---
    list_display = (
        "identificacion",
        "nombres",
        "apellidos",
        "get_nombre_representante",
        "get_telefono_representante",
        
        
    )

    search_fields = ("identificacion", "nombres", "apellidos")

    list_per_page = 20

    # --- Fieldsets (Formulario) ---
    fieldsets = (
        (
            "Identificación",
            {"fields": ("identificacion", "parroquia_actual_ref_id")},
        ),  # <--- Y AQUÍ
        (
            "Información Personal",
            {
                "fields": ("nombres", "apellidos", "fecha_nacimiento"),
                "classes": ("wide",),
            },
        ),
        ("Datos Embebidos", {"fields": ("representante", "datos_bautismo")}),
        ("Movimientos", {"fields": ("historial_traslados",), "classes": ("collapse",)}),
    )

    # --- MÉTODOS BLINDADOS (Soportan Objetos y Diccionarios) ---

    @admin.display(description="Representante")
    def get_nombre_representante(self, obj):
        rep = obj.representante
        if not rep:
            return "-"

        # Caso 1: Es un Diccionario (JSON crudo de Mongo)
        if isinstance(rep, dict):
            return rep.get("nombre", "-")

        # Caso 2: Es un Objeto Django (Instancia de modelo)
        return getattr(rep, "nombre", "-")

    @admin.display(description="Tel. Representante")
    def get_telefono_representante(self, obj):
        rep = obj.representante
        if not rep:
            return "-"

        # Caso 1: Es un Diccionario
        if isinstance(rep, dict):
            return rep.get("telefono", "-")

        # Caso 2: Es un Objeto Django
        return getattr(rep, "telefono", "-")
