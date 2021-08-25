from django.contrib import admin

# Register your models here.
from countries.models import Country


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    search_fields = ['title']
