from django import template

from news.models import Rubric

register = template.Library()


@register.simple_tag
def menu_builder():
    return Rubric.objects.all()