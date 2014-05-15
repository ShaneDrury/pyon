from django.core.management.templates import TemplateCommand


class Command(TemplateCommand):
    def handle(self, *args, **options):
        raise NotImplementedError
