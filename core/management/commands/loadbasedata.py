from django.core.management.base import BaseCommand, CommandError
from core.scripts import loadbasedata

class Command(BaseCommand):
    help = 'Load initial data into database'

    def handle(self, *args, **options):
        loadbasedata()

        
