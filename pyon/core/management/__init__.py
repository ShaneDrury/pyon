import os
import sys
import collections
import six

#  I don't think this is necessary. In fact it probably shouldn't be here since
#  the user may be running the script from within their app in which case they
#  will want their own settings here.
#  django.conf.settings uses whatever settings module is in the environment
#  variable
#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django.conf.global_settings")

from django.conf import settings
from django.core import management
settings.configure()  # Fixes the warning line... I don't know why though.


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

    def main_help_text(self, commands_only=False):
        """
        Returns the script's main help text, as a string.
        """
        if commands_only:
            usage = sorted(get_commands().keys())
        else:
            usage = [
                "",
                "Type '%s help <subcommand>' for help on a specific subcommand." % self.prog_name,
                "",
                "Available subcommands:",
            ]
            commands_dict = collections.defaultdict(lambda: [])
            for name, app in six.iteritems(get_commands()):
                if app == 'pyon.core' or app == "django.core":
                    app = 'pyon'
                else:
                    app = app.rpartition('.')[-1]
                commands_dict[app].append(name)
            style = management.color_style()
            for app in sorted(commands_dict.keys()):
                usage.append("")
                usage.append(style.NOTICE("[%s]" % app))
                for name in sorted(commands_dict[app]):
                    usage.append(" %s" % name)
            # Output an extra note if settings are not properly configured
            try:
                settings.INSTALLED_APPS
            except management.ImproperlyConfigured as e:
                usage.append(style.NOTICE(
                    "Note that only Django core commands are listed as settings"
                    "are not properly configured (error: %s)." % e))

        return '\n'.join(usage)

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
    utility = ManagementUtility(argv)
    utility.execute()
