from __future__ import unicode_literals

from django.contrib.auth.models import User
# from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from mptt.models import MPTTModel, TreeForeignKey

from core.models import Votable, Vote


class Comment(MPTTModel, Votable):
    author = models.ForeignKey(User, verbose_name="Автор", on_delete=models.CASCADE)
    text = models.CharField(verbose_name="Сообщение", max_length=1000)
    created = models.DateTimeField(verbose_name="Создан", editable=False)
    # edited = models.DateTimeField()
    parent = TreeForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='children',
        db_index=True, on_delete=models.CASCADE
    )
    moderated = models.BooleanField(
        verbose_name="Прошёл модерацию",
        editable=True,
        default=True
    )

    # Content type  base fields
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return "%s - %s" % (self.created, self.author)

    def save(self, created_insert=False, **kwargs):
        if not self.id:
            if created_insert is False:
                self.created = timezone.now()

            if self.parent:
                self.object_id = self.parent.object_id

        return super(Comment, self).save(**kwargs)

    def get_user(self):

        try:
            user = User.objects.get(id=self.author.id)
        except User.DoesNotExist:
            return None
        return user

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ['-created', ]


class CommentVoteManager(models.Manager):
    def get_query_set(self):
        ctype = ContentType.objects.get_for_model(Comment)
        qs = super(CommentVoteManager, self).get_query_set().filter(
            content_type=ctype
        )
        return qs


class CommentVote(Vote):
    objects = CommentVoteManager()

    def save(self):
        if not self.id:
            ctype = ContentType.objects.get_for_model(Comment)
            self.content_type = ctype
        return super(CommentVote, self).save()

    class Meta:
        proxy = True


class ObsceneWord(models.Model):
    chars = models.CharField(
        verbose_name="составляющая нецензурного слова",
        max_length=200,
        help_text="""Каждая буква и вариация пишется через пробел
        (например "с у к а"),
        если у буквы есть вариации, то пишутся вместе, без пробела
        (напр. "п еи д о р а с", в такой фильтр будут попадать слова
        "пидорас" и "педорас")
        Регистр букв не нужно указывать (не надо писать "Сс Уу Кк Аа")
        """)

    def __str__(self):
        return self.chars

    class Meta:
        verbose_name = "Матерное слово"
        verbose_name_plural = "Матерные слова"
        ordering = ["chars", ]
