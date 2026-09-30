from django.apps import AppConfig


class PagesConfig(AppConfig):
    name = "pages"

    def ready(self):
        from .pybryt_patch import patch_pybryt_execute_notebook

        patch_pybryt_execute_notebook()