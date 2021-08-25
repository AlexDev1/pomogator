from news.models import Rubric


def run():
    for rubric in Rubric.objects.all():
        rubric.slug = rubric.title_en
        rubric.save()
