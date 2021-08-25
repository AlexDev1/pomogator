# Generated by Django 3.2.6 on 2021-08-25 09:59

import core.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import photologue.models
import tinymce.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('countries', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('photologue', '0012_auto_20210825_0959'),
        ('comments', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pubdate', models.DateTimeField(auto_created=True, verbose_name='Дата публикаци')),
                ('count_visits', models.PositiveIntegerField(default=0, editable=False, verbose_name='Счетчик просмотров')),
                ('fake_visits', models.PositiveIntegerField(default=0, verbose_name='Псевдо')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Создан')),
                ('modified', models.DateTimeField(blank=True, null=True, verbose_name='Отредактирован')),
                ('title', models.CharField(max_length=200, verbose_name='Заголовок')),
                ('subtitle', models.CharField(blank=True, max_length=200, null=True, verbose_name='Подзаголовок')),
                ('text', tinymce.models.HTMLField(verbose_name='Тескт')),
                ('published', models.BooleanField(db_index=True, default=False, verbose_name='Опубликовано')),
                ('rss_exclude', models.BooleanField(default=False, verbose_name='Исключить из RSS')),
                ('countries', models.ManyToManyField(blank=True, to='countries.Country', verbose_name='Страны')),
            ],
            options={
                'verbose_name': 'Статья',
                'verbose_name_plural': 'Статьи',
                'db_table': 'articles_article',
                'ordering': ('-pubdate',),
            },
        ),
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=150, verbose_name='Имя и фамилия')),
                ('active', models.BooleanField(verbose_name='Активный')),
            ],
            options={
                'verbose_name': 'Автор новости',
                'verbose_name_plural': 'Авторы новостей',
            },
        ),
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count_visits', models.PositiveIntegerField(default=0, editable=False, verbose_name='Счетчик просмотров')),
                ('fake_visits', models.PositiveIntegerField(default=0, verbose_name='Псевдо')),
                ('title', models.CharField(max_length=200, verbose_name='Заголовок')),
                ('subtitle', models.CharField(blank=True, max_length=200, null=True, verbose_name='Подзаголовок')),
                ('pubdate', models.DateTimeField(db_index=True, verbose_name='Дата публикации')),
                ('delayed_publication', models.BooleanField(db_index=True, default=False, verbose_name='Отложенная публикация')),
                ('text', tinymce.models.HTMLField(verbose_name='Тескт')),
                ('published', models.BooleanField(db_index=True, default=False, verbose_name='Опубликовано')),
                ('rss_exclude', models.BooleanField(default=False, verbose_name='Исключить из RSS')),
                ('youtube_video', models.URLField(blank=True, help_text='Ссылка на видео с youtube.com', max_length=1024, verbose_name='Ссылка на видео')),
                ('modified_value', models.DateTimeField(auto_now=True, verbose_name='Изменено')),
                ('authors', models.ManyToManyField(blank=True, to='news.Author', verbose_name='Авторы')),
                ('countries', models.ManyToManyField(to='countries.Country', verbose_name='Страны')),
            ],
            options={
                'verbose_name': 'Новость',
                'verbose_name_plural': 'Новости',
                'ordering': ('-pubdate',),
            },
            bases=(core.fields.YoutubeVideoLinkMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Rubric',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveSmallIntegerField(default=0, verbose_name='Сортировка')),
                ('title', models.CharField(max_length=50, verbose_name='Название')),
                ('title_en', models.CharField(db_index=True, max_length=50, verbose_name='Название (англ.)')),
                ('text', models.TextField(verbose_name='Описание')),
                ('slug', models.SlugField()),
                ('last_update', models.DateTimeField(blank=True, null=True, verbose_name='Изменено')),
            ],
            options={
                'verbose_name': 'Рубрика новости',
                'verbose_name_plural': 'Рубрики новостей',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Source',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, verbose_name='Название')),
                ('url', models.CharField(max_length=150, verbose_name='URL')),
            ],
            options={
                'verbose_name': 'Источник',
                'verbose_name_plural': 'Источники',
            },
        ),
        migrations.CreateModel(
            name='SpecialBlock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, verbose_name='Название')),
                ('lastnews_date', models.DateTimeField(blank=True, null=True, verbose_name='Дата последней новости')),
            ],
            options={
                'verbose_name': 'Специальный блок новостей',
                'verbose_name_plural': 'Специальные блоки новостей',
                'ordering': ('-lastnews_date',),
            },
        ),
        migrations.CreateModel(
            name='Stories',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=150, verbose_name='Название')),
                ('active', models.BooleanField(verbose_name='Актуальный')),
                ('slug', models.SlugField(blank=True, max_length=150, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='', verbose_name='Картинка')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Описание')),
                ('order', models.PositiveSmallIntegerField(db_index=True, default=0, verbose_name='Order')),
            ],
            options={
                'verbose_name': 'Сюжет новости',
                'verbose_name_plural': 'Сюжеты новостей',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='NewsNewComment',
            fields=[
            ],
            options={
                'verbose_name': 'Комментарий к новости',
                'verbose_name_plural': 'Комментарии к новости',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('comments.comment',),
        ),
        migrations.CreateModel(
            name='NewsPhoto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to=photologue.models.get_storage_path, verbose_name='image')),
                ('date_taken', models.DateTimeField(blank=True, help_text='Date image was taken; is obtained from the image EXIF data.', null=True, verbose_name='date taken')),
                ('view_count', models.PositiveIntegerField(default=0, editable=False, verbose_name='view count')),
                ('crop_from', models.CharField(blank=True, choices=[('top', 'Top'), ('right', 'Right'), ('bottom', 'Bottom'), ('left', 'Left'), ('center', 'Center (Default)')], default='center', max_length=10, verbose_name='crop from')),
                ('photo_type', models.SmallIntegerField(choices=[(0, '---'), (1, 'Верхнее фото'), (2, 'Маленькое превью'), (3, 'Большое превью'), (4, 'Нижнее фото')], default=0, verbose_name='Тип фото')),
                ('description', models.CharField(blank=True, max_length=200, null=True, verbose_name='Описание')),
                ('effect', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='newsphoto_related', to='photologue.photoeffect', verbose_name='effect')),
                ('news', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='news.news')),
            ],
            options={
                'verbose_name': 'Фотография новости',
                'verbose_name_plural': 'Фотографии новости',
            },
        ),
        migrations.AddField(
            model_name='news',
            name='rubrics',
            field=models.ManyToManyField(related_name='rubrics', to='news.Rubric', verbose_name='Рубрики для новости'),
        ),
        migrations.AddField(
            model_name='news',
            name='special_blocks',
            field=models.ManyToManyField(blank=True, related_name='news', to='news.SpecialBlock', verbose_name='Спецблоки'),
        ),
        migrations.AddField(
            model_name='news',
            name='stories',
            field=models.ManyToManyField(blank=True, related_name='stories', to='news.Stories', verbose_name='Сюжеты'),
        ),
        migrations.AddField(
            model_name='news',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.CreateModel(
            name='ArticleImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='articles', verbose_name='Изображение статьи')),
                ('description', models.CharField(blank=True, max_length=200, null=True, verbose_name='Описание')),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='news.article')),
            ],
            options={
                'verbose_name': 'Изображения статьи',
                'verbose_name_plural': 'Изображения статей',
            },
        ),
        migrations.AddField(
            model_name='article',
            name='rubrics',
            field=models.ManyToManyField(to='news.Rubric', verbose_name='Рубрики'),
        ),
        migrations.AddField(
            model_name='article',
            name='script_country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='article_script_country', to='countries.country', verbose_name='Виджет скрипт для страны'),
        ),
        migrations.AddField(
            model_name='article',
            name='special_blocks',
            field=models.ManyToManyField(blank=True, related_name='articles', to='news.SpecialBlock', verbose_name='Спецблоки'),
        ),
        migrations.AddField(
            model_name='article',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.CreateModel(
            name='NewsTopPicture',
            fields=[
                ('image', models.ImageField(upload_to=photologue.models.get_storage_path, verbose_name='image')),
                ('date_taken', models.DateTimeField(blank=True, help_text='Date image was taken; is obtained from the image EXIF data.', null=True, verbose_name='date taken')),
                ('view_count', models.PositiveIntegerField(default=0, editable=False, verbose_name='view count')),
                ('crop_from', models.CharField(blank=True, choices=[('top', 'Top'), ('right', 'Right'), ('bottom', 'Bottom'), ('left', 'Left'), ('center', 'Center (Default)')], default='center', max_length=10, verbose_name='crop from')),
                ('news', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='news.news', verbose_name='Новость')),
                ('description', models.CharField(blank=True, max_length=200, null=True, verbose_name='Подпись')),
                ('effect', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='newstoppicture_related', to='photologue.photoeffect', verbose_name='effect')),
            ],
            options={
                'verbose_name': 'Верхнее фото',
                'verbose_name_plural': 'Верхнее фото',
            },
        ),
        migrations.CreateModel(
            name='NewsSmallPreview',
            fields=[
                ('image', models.ImageField(upload_to=photologue.models.get_storage_path, verbose_name='image')),
                ('date_taken', models.DateTimeField(blank=True, help_text='Date image was taken; is obtained from the image EXIF data.', null=True, verbose_name='date taken')),
                ('view_count', models.PositiveIntegerField(default=0, editable=False, verbose_name='view count')),
                ('crop_from', models.CharField(blank=True, choices=[('top', 'Top'), ('right', 'Right'), ('bottom', 'Bottom'), ('left', 'Left'), ('center', 'Center (Default)')], default='center', max_length=10, verbose_name='crop from')),
                ('news', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='news.news', verbose_name='Новость')),
                ('effect', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='newssmallpreview_related', to='photologue.photoeffect', verbose_name='effect')),
            ],
            options={
                'verbose_name': 'Маленькое превью',
                'verbose_name_plural': 'Маленькое превью',
            },
        ),
        migrations.CreateModel(
            name='NewsBottomPicture',
            fields=[
                ('image', models.ImageField(upload_to=photologue.models.get_storage_path, verbose_name='image')),
                ('date_taken', models.DateTimeField(blank=True, help_text='Date image was taken; is obtained from the image EXIF data.', null=True, verbose_name='date taken')),
                ('view_count', models.PositiveIntegerField(default=0, editable=False, verbose_name='view count')),
                ('crop_from', models.CharField(blank=True, choices=[('top', 'Top'), ('right', 'Right'), ('bottom', 'Bottom'), ('left', 'Left'), ('center', 'Center (Default)')], default='center', max_length=10, verbose_name='crop from')),
                ('news', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='news.news', verbose_name='Новость')),
                ('description', models.CharField(blank=True, max_length=200, null=True, verbose_name='Подпись')),
                ('effect', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='newsbottompicture_related', to='photologue.photoeffect', verbose_name='effect')),
            ],
            options={
                'verbose_name': 'Нижнее фото',
                'verbose_name_plural': 'Нижнее фото',
            },
        ),
        migrations.CreateModel(
            name='NewsBigPreview',
            fields=[
                ('image', models.ImageField(upload_to=photologue.models.get_storage_path, verbose_name='image')),
                ('date_taken', models.DateTimeField(blank=True, help_text='Date image was taken; is obtained from the image EXIF data.', null=True, verbose_name='date taken')),
                ('view_count', models.PositiveIntegerField(default=0, editable=False, verbose_name='view count')),
                ('crop_from', models.CharField(blank=True, choices=[('top', 'Top'), ('right', 'Right'), ('bottom', 'Bottom'), ('left', 'Left'), ('center', 'Center (Default)')], default='center', max_length=10, verbose_name='crop from')),
                ('news', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='news.news', verbose_name='Новость')),
                ('effect', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='newsbigpreview_related', to='photologue.photoeffect', verbose_name='effect')),
            ],
            options={
                'verbose_name': 'Большое превью',
                'verbose_name_plural': 'Большое превью',
            },
        ),
    ]