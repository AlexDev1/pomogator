from django.db.models.signals import post_save
from django.dispatch import receiver

from news.models import News, Rubric


@receiver(post_save, sender=News)
def post_save_news(sender, instance, created, **kwargs):
    instance.rubrics.update(last_update=instance.modified_value)
    instance.countries.update(last_update_news=instance.modified_value)

