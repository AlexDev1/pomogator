from news.models import News
from pomogator.celery import app


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls every 10 seconds.
    sender.add_periodic_task(10.0, publish_news_pomogator.s(), name='add every 10')


@app.task
def publish_news_pomogator():
    news = News.objects.all_objects().filter(delayed_publication=True, published=False)
    from django.utils import timezone
    today = timezone.now()
    for i in news:
        if i.pubdate <= today:
            i.published = True
            i.delayed_publication = False
            i.save()


