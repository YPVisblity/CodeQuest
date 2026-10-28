from django.apps import AppConfig


class PagesConfig(AppConfig):
    name = "pages"

    def ready(self):
        from .pybryt_patch import patch_pybryt_execute_notebook
        from . import signals  # noqa: F401  註冊 allauth 的 signal

        patch_pybryt_execute_notebook()