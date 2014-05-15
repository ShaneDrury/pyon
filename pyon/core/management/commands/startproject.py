import os
from django.core.management.base import CommandError
from django.core.management.templates import TemplateCommand
from django.utils.crypto import get_random_string
from django.utils.importlib import import_module
import pyon


class Command(TemplateCommand):
    help = ("Creates a Pyon project directory structure for the given "
            "project name in the current directory or optionally in the "
            "given directory.")

    def handle(self, project_name=None, target=None, *args, **options):
        self.validate_name(project_name, "project")

        # Check that the project_name cannot be imported.
        try:
            import_module(project_name)
        except ImportError:
            pass
        else:
            raise CommandError("%r conflicts with the name of an existing "
                               "Python module and cannot be used as a "
                               "project name. Please try another name." %
                               project_name)

        # Create a random SECRET_KEY hash to put it in the main settings.
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        options['secret_key'] = get_random_string(50, chars)
        options['template'] = os.path.join(pyon.__path__[0], 'conf', 'project_template')
        super(Command, self).handle('project', project_name, target, **options)
