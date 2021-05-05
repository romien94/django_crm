from django.core.management.base import BaseCommand
from leads.models import Lead, UserProfile
from csv import DictReader


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('file_name', type=str)
        parser.add_argument('organizer_email', type=str)

    def handle(self, *args, **options):
        file_name = options.get('file_name')
        organizer_email = options.get('organizer_email')
        organization = UserProfile.objects.get(user__email=organizer_email)

        with open(file_name, 'r') as f:
            csv_data = DictReader(f)
            for lead in csv_data:
                Lead.objects.create(**lead, organization=organization)

        return f'The leads from the {file_name} has been successfully created'
