# -*- coding: utf-8 -*-
import requests
from django.core.management.base import BaseCommand

from countries.models import Country


class Command(BaseCommand):

    def execute(self, *args, **options):
        api_uri = 'https://www.tourprom.ru/api/v1/countries/'
        json_data = requests.get(api_uri).json()
        for data in json_data:
            Country.objects.get_or_create(**data)
