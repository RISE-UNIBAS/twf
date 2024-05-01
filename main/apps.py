"""Configuration of the project"""
from django.apps import AppConfig


class MainConfig(AppConfig):
    """Configuration of the project"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "main"

    def ready(self):
        import main.signals
