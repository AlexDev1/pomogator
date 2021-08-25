from adminsortable2.admin import SortableInlineAdminMixin
from django.contrib import admin

from partners.models import PartnerWidgetScript, PartnerPage


class PartnerWidgetScriptAdmin(SortableInlineAdminMixin, admin.TabularInline):
    model = PartnerWidgetScript
    extra = 1


@admin.register(PartnerPage)
class PartnerPageAdmin(admin.ModelAdmin):
    list_display_links = ["title"]
    list_display = ["id", "title", "slug"]
    search_fields = ["title"]

    inlines = [PartnerWidgetScriptAdmin, ]
    fieldsets = (
        ('Основные данные', {'fields': (
            'title', 'subtitle', 'disc', 'news_subjects', 'slug'
        )}),
        ('SEO', {'fields': ('meta_title', 'meta_description', 'meta_keywords'),
                 'classes': ['collapse', ]}),
    )
