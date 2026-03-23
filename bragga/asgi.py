"""
ASGI config for bragga project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    os.getenv("DJANGO_SETTINGS_MODULE", "bragga.settings.dev")
)

application = get_asgi_application()