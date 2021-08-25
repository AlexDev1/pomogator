# Generated by Django 3.2.6 on 2021-08-25 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('voteups', models.IntegerField(default=0, editable=False, verbose_name='Количесвто лайков')),
                ('votedowns', models.IntegerField(default=0, editable=False, verbose_name='Количесвто дислайков')),
                ('text', models.CharField(max_length=1000, verbose_name='Сообщение')),
                ('created', models.DateTimeField(editable=False, verbose_name='Создан')),
                ('moderated', models.BooleanField(default=True, verbose_name='Прошёл модерацию')),
                ('object_id', models.PositiveIntegerField()),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
            ],
            options={
                'verbose_name': 'Комментарий',
                'verbose_name_plural': 'Комментарии',
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='ObsceneWord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chars', models.CharField(help_text='Каждая буква и вариация пишется через пробел\n        (например "с у к а"),\n        если у буквы есть вариации, то пишутся вместе, без пробела\n        (напр. "п еи д о р а с", в такой фильтр будут попадать слова\n        "пидорас" и "педорас")\n        Регистр букв не нужно указывать (не надо писать "Сс Уу Кк Аа")\n        ', max_length=200, verbose_name='составляющая нецензурного слова')),
            ],
            options={
                'verbose_name': 'Матерное слово',
                'verbose_name_plural': 'Матерные слова',
                'ordering': ['chars'],
            },
        ),
    ]