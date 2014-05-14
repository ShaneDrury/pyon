import collections
from django.core import management
import sys
from django.utils import six


def get_commands():
    commands = {name: 'pyon.core'
                for name in management.find_commands(__path__[0])}
    django_commands = management.get_commands()
    django_commands.update(commands)
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
