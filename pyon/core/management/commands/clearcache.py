import logging
from django.core.management import BaseCommand
from pyon.core.cache import cache
log = logging.getLogger(__name__)


class Command(BaseCommand):
    args = '<key1 key2 ...>'
    help = 'Clears the specific caches'

    def handle(self, *args, **options):
        if 'all' in args or args is ():
            self.clear_all()
        else:
            log.info("Clearing {}".format(args))
            cache.delete_many(args)

    def clear_all(self):
        log.info("Clearing entire cache")
        cache.clear()
