#!/usr/bin/env python
import os
import sys
import logging
from {{ project_name }} import settings
if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "{{ project_name }}.settings")
    logging.basicConfig(level=settings.LOGGING_LEVEL)
    from pyon.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
