from django.core.management import BaseCommand
from pyon.core.cache import cache


class Command(BaseCommand):
    args = '<key1 key2 ...>'
    help = 'Clears the specific caches'

    def handle(self, *args, **options):
        if 'all' in args:
            cache.clear()
        else:
            cache.delete_many(args)