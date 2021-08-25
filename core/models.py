from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Vote(models.Model):
    """
    Нравится/Не нравится
    """
    user = models.ForeignKey(
        User,
        related_name='votes',
        verbose_name=u'Пользователь', on_delete=models.CASCADE
    )
    content_type = models.ForeignKey(ContentType, verbose_name=u'Тип объекта', on_delete=models.CASCADE)
    object_id = models.IntegerField(verbose_name=u'Объект')
    content_object = GenericForeignKey('content_type', 'object_id')
    datetime = models.DateTimeField(u'Дата', auto_now_add=True)
    like = models.SmallIntegerField(
        verbose_name='Нравится/Не нравится',
        choices=(
            (-1, '-'),
            (1, '+')
        )
    )

    def __str__(self):
        return u'%s' % self.content_object

    def save(self, *args, **kwargs):
        super(Vote, self).save(*args, **kwargs)
        if hasattr(self.content_object, 'recount_votes'):
            self.content_object.recount_votes()

    def object_type(self):
        if self.content_type.model.endswith('review'):
            return 'review'
        if self.content_type.model.endswith('comment'):
            return 'comment'
        return None

    class Meta:
        app_label = 'countries'


class Votable(models.Model):
    """Abstarct model to implements votes up and down"""

    voteups = models.IntegerField(
        u'Количесвто лайков', editable=False, default=0)
    votedowns = models.IntegerField(
        u'Количесвто дислайков', editable=False, default=0)

    class Meta:
        abstract = True

    def recount_votes(self):
        ctype = ContentType.objects.get_for_model(self)
        votes = Vote.objects.filter(content_type=ctype, object_id=self.id)
        ups = votes.filter(like__gt=0).count()
        downs = votes.filter(like__lt=0).count()
        self.__class__.objects.filter(id=self.id)\
            .update(voteups=ups, votedowns=downs)
