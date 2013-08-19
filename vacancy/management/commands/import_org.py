import csv
from django.core.management.base import BaseCommand
from vacancy.models import Organization, SocialLink


class Command(BaseCommand):
    args = '<file>'
    help = 'Imports organizations from CSV file'

    def handle(self, *args, **options):
        file_name = args[0]
        with open(file_name, 'r') as org_file:
            org_reader = csv.reader(org_file, delimiter=',', quotechar='"', doublequote=True)
            org_reader.next()
            for row in org_reader:
                organization = Organization(title=row[0], slogan=row[1], description=row[2], phone_number=row[4],
                                            email=row[5], address_line=row[6], web_site=row[7])
                organization.save()
                if row[8]:
                    social_link = SocialLink(organization=organization, network='vkontakte', identity=row[8])
                    social_link.save()
                if row[9]:
                    social_link = SocialLink(organization=organization, network='facebook', identity=row[9])
                    social_link.save()
