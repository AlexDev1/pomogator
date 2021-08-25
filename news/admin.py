from datetime import datetime
from adminsortable2.admin import SortableAdminMixin
from daterangefilter.filters import DateRangeFilter
from django import forms
from django.contrib import admin
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage
from django.db import models
from django.forms import ModelMultipleChoiceField
from django_toggle_switch_widget.widgets import DjangoToggleSwitchWidget
from tinymce import TinyMCE

from core.admin import MultipleChoiceListFilter
from news.models import News, Stories, Rubric, Source, Author, NewsPhoto, Article, ArticleImage, SpecialBlock


class SelectWithDisabled(forms.SelectMultiple):
    def __init__(self, attrs=None, choices=()):
        self.custom_attrs = {}
        super().__init__(attrs, choices)

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if value.value in self.custom_attrs:
            option['attrs'].update({k: v for k, v in self.custom_attrs[value.value].items()})
            option['attrs'].update({'disabled': True if not option['attrs']['data-active'] else False})
        return option


class ModelChoiceFieldWithData(ModelMultipleChoiceField):
    widget = SelectWithDisabled

    def __init__(self, *args, **kwargs):
        self.additional_data = kwargs.pop('additional_data')
        super().__init__(*args, **kwargs)

    # пользовательский метод для обозначения параметра поля
    def label_from_instance(self, obj):
        # так как объект доступен здесь, можно установить дополнительные атрибуты
        self.widget.custom_attrs[obj.pk] = {f'data-{attr}': getattr(obj, attr) for attr in self.additional_data}
        return super().label_from_instance(obj)


class NewsAdminForm(forms.ModelForm):
    publish_field = forms.BooleanField(label="Публикация", required=False)
    stories = ModelChoiceFieldWithData(queryset=Stories.objects.all().order_by('-active'),
                                       help_text='Удерживайте "Control" (или "Command" на Mac), '
                                                 'чтобы выбрать несколько значений.',
                                       label='Сюжеты', required=False,
                                       additional_data=('active',))

    class Meta:
        model = News
        exclude = ('newsmakers',)
        widgets = {
            'title': forms.TextInput(attrs={'size': 100}),
            'subtitle': forms.TextInput(attrs={'size': 70}),
            "published": DjangoToggleSwitchWidget(klass="django-toggle-switch-dark-primary", round=True),
            "delayed_publication": DjangoToggleSwitchWidget(klass="django-toggle-switch-dark-primary", round=True),
        }

    def clean(self):
        cleaned_data = super(NewsAdminForm, self).clean()
        from django.utils import timezone
        today = timezone.now()
        if today >= cleaned_data['pubdate'] and cleaned_data['delayed_publication'] == True:
            from django.forms import ValidationError
            raise ValidationError('При отложенной публикации дата должна быть больше текущей')
        return cleaned_data


class NewsPhotoInline(admin.TabularInline):
    model = NewsPhoto
    fields = [
        'image',
        'description',
    ]


class AuthorListFilter(MultipleChoiceListFilter):
    title = 'Авторы'
    parameter_name = 'authors__in'

    def lookups(self, request, model_admin):
        authors = Author.objects.filter(active=True).order_by('full_name')
        for author in authors:
            yield (str(author.id), author.full_name)
        # return Author.objects.all()


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    autocomplete_fields = ['countries', 'authors', ]
    form = NewsAdminForm
    search_fields = ["title", ]
    list_display_links = ('title',)
    # list_display = ('pubdate', 'title', 'published', 'count_visits', 'fake_visits')
    list_display = ('get_pubdate', 'admin_cover', 'title', 'published', 'count_visits', 'fake_visits')
    raw_id_fields = ['user']
    inlines = [NewsPhotoInline, ]
    list_filter = ['published', ('pubdate', DateRangeFilter), AuthorListFilter]
    readonly_fields = (
        'count_visits',
        'fake_visits',
        # 'user'
    )
    fields = ['title', 'subtitle', 'pubdate',
              ('publish_field', 'published', 'delayed_publication',),
              'text', 'authors', 'countries', 'rubrics', 'stories',
              'rss_exclude', 'youtube_video', 'special_blocks', 'user',
              'count_visits', 'fake_visits']

    # def get_fields(self, request, obj):
    #     fields = super().get_fields(request, obj)
    #     print(fields)
    #     return fields

    def get_queryset(self, request):
        qs = self.model.objects.all_objects()
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def save_model(self, request, obj, form, change):
        rval = super(NewsAdmin, self).save_model(request, obj, form, change)
        is_superuser = request.user.is_superuser
        if not is_superuser:
            obj.user = request.user
            obj.save()
        return rval

    def get_form(self, request, obj=None, **kwargs):
        """
        Проверяем пользователя, если пользователь не Админ, то запрещаем публиковать новости
        :param request:
        :param obj:
        :param kwargs:
        :return:
        """
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        form.base_fields['published'].label = 'Опубликовать сразу'
        disabled_fields = set()  # type: Set[str]

        if not is_superuser:
            disabled_fields |= {
                'published', 'is_main', 'rss_exclude', 'user'
            }
            # readonly_fields = list(self.readonly_fields)
            # readonly_fields.append('user')
            # self.readonly_fields = readonly_fields

        for f in disabled_fields:
            if f in form.base_fields:
                form.base_fields[f].disabled = True
        return form

    def get_row_css(self, obj, index):
        from django.utils import timezone
        today = timezone.now()
        if obj.published and obj.pubdate <= today:
            return 'publish-news publish-news%d' % index
        elif obj.delayed_publication and today <= obj.pubdate:
            return 'delayed-published-news delayed-published-news%d' % index
        elif not obj.published:
            return 'unpublished-news unpublished-news%d' % index
        return ''

    class Media:
        css = {
            'all': ('/static/admin_static/admin.css',),
        }

        js = ('/static/admin_static/js/news_delayed.js',)


@admin.register(Stories)
class AdminStories(admin.ModelAdmin):
    list_display = ['title', 'active', 'count_new']
    prepopulated_fields = {'slug': ('title',),}


@admin.register(Rubric)
class AdminRubric(SortableAdminMixin, admin.ModelAdmin):
    list_display = ['order', 'title', 'last_update']
    list_display_links = ['title']
    readonly_fields = ['last_update']


@admin.register(Source)
class AdminSource(admin.ModelAdmin):
    list_display = ['name', 'url', ]


@admin.register(Author)
class AdminAuthor(admin.ModelAdmin):
    search_fields = ['full_name']
    list_display = ['full_name', 'active']


class ArticleImageAdmin(admin.TabularInline):
    model = ArticleImage


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    # form = ArticleAdminForm
    # autocomplete_fields = ['countries', 'resorts', 'regions', 'script_country']
    # raw_id_fields = ('resorts', 'regions', 'advertiser', 'photogallery')
    inlines = (ArticleImageAdmin,)
    readonly_fields = (
        # 'created',
        'modified',
        'fake_visits',
        'count_visits',
    )
    list_display = (
        'title',
        'pubdate', 'published',
        'count_visits', 'fake_visits'
    )

    def get_queryset(self, request):
        qs = super(ArticleAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def save_model(self, request, obj, form, change):
        rval = super(ArticleAdmin, self).save_model(request, obj, form, change)
        is_superuser = request.user.is_superuser
        if not is_superuser:
            obj.user = request.user
            obj.save()
        return rval


@admin.register(SpecialBlock)
class SpecialBlockAdmin(admin.ModelAdmin):
    list_display = ('name', 'lastnews_date')



# Register your models here.
class PageAdmin(FlatPageAdmin):
    """Page Admin"""

    formfield_overrides = {
        models.TextField: {'widget': TinyMCE(attrs={'cols': 100, 'rows': 15})},
    }


admin.site.unregister(FlatPage)
admin.site.register(FlatPage, PageAdmin)
