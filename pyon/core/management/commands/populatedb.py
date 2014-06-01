from django.core.management import BaseCommand
from django.conf import settings
from pyon.core.project import Project
import logging


class Command(BaseCommand):
    def handle(self, *args, **options):
        logging.basicConfig(level=settings.LOGGING_LEVEL,
                            format=settings.LOGGING_FORMAT,
                            datefmt=settings.LOGGING_DATEFMT,
                            filename=settings.LOGGING_FILE)
        project = Project(name=settings.PROJECT_NAME,
                          dump_dir=settings.DUMP_DIR)
        project.populatedb()
