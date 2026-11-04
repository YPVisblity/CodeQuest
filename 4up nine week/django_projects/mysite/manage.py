#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    if len(sys.argv) > 1 and sys.argv[1] == 'compile-assignment-reference':
        # Keep reference conversion in a child process without another module file.
        if len(sys.argv) != 4:
            raise SystemExit('Usage: manage.py compile-assignment-reference input.ipynb output.pkl')
        import django
        django.setup()
        from pages.views import _compile_assignment_reference
        _compile_assignment_reference(sys.argv[2], sys.argv[3])
        return
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
