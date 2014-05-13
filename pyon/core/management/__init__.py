import os
import sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django.conf.global_settings")

from django.core import management

def get_commands():

    django_commands \
      = {name: 'django.core'
         for name in management.find_commands(management.__path__[0])}

    commands = {name: 'pyon.core'
                for name in management.find_commands(__path__[0])}

    django_commands.update(commands)
    """
    ## STUFF TO BE FINISHED LATER!!!
    try:
        settings.INSTALLED_APPS
    except management.ImproperlyConfigured:
        app_names = []
    else:
        app_configs = apps.get_app_configs()
        app_names = [app_config.name for app_config in app_configs]

    for app_name in reversed(app_names):
        try:
            path = find_management_module(app_name)
            commands.update({name: app_name for name in find_commands(path)})
        except ImportError:
            pass # No management module - ignore this app
    """
    return django_commands

class ManagementUtility(management.ManagementUtility):

    def fetch_command(self, subcommand):
        
        commands = get_commands()
        
        try:
            app_name = commands[subcommand]
        except KeyError:
            sys.stderr.write("Unknown command: %r\nType '%s help' for usage.\n" %
                (subcommand, self.prog_name))
            sys.exit(1)

        if isinstance(app_name, management.BaseCommand):
            klass = app_name
        else:
            klass = management.load_command_class(app_name, subcommand)

        return klass
        
def execute_from_command_line(argv=None):
    """
    A simple method that runs a ManagementUtility.
    """
    print("TADA")
    utility = ManagementUtility(argv)
    utility.execute()
