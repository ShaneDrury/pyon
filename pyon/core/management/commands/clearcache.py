from django.core.management import BaseCommand
from pyon.core.cache import cache


class Command(BaseCommand):
    def handle(self, *args, **options):
        cache.clear()