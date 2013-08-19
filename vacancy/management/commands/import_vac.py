# coding=utf-8
import csv
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from vacancy.models import Organization, SocialLink, Vacancy


class Command(BaseCommand):
    args = '<file>'
    help = 'Imports vacancies from CSV file'

    def handle(self, *args, **options):
        file_name = args[0]
        with open(file_name, 'r') as org_file:
            org_reader = csv.reader(org_file, delimiter=',', quotechar='"', doublequote=True)
            org_reader.next()
            for row in org_reader:
                try:
                    organization = Organization.objects.get(title=row[0])
                except ObjectDoesNotExist:
                    continue
                for i in range(5):
                    if not row[1 + i * 3]:
                        continue
                    vacancy = Vacancy(title=row[1 + i * 3], description=row[2 + i * 3],
                                      is_continuous=(row[3 + i * 3] == u'постоянная'.encode('utf-8')),
                                      organization=organization)
                    vacancy.save()
