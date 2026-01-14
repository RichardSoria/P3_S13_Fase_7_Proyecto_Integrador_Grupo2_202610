"""
ASGI config for P3_S13_Fase_7_Proyecto_Integrador_Grupo2_202610 project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'P3_S13_Fase_7_Proyecto_Integrador_Grupo2_202610.settings')

application = get_asgi_application()
