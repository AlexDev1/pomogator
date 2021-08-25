from adminsortable2.admin import SortableInlineAdminMixin
from django.contrib import admin
from django.utils.safestring import mark_safe

from banner.models import WidgetScript, WidgetRegion
from core.admin import ListStyleAdminMixin


class WidgetScriptAdmin(SortableInlineAdminMixin, admin.TabularInline):
    model = WidgetScript
    extra = 1


@admin.register(WidgetRegion)
class WidgetRegionAdmin(ListStyleAdminMixin, admin.ModelAdmin):
    list_display = ('section', 'title', 'active', 'names_script')
    # autocomplete_fields = ['country']
    list_display_links = ['section', 'title']
    list_filter = ['section']
    inlines = [WidgetScriptAdmin, ]

    def names_script(self, obj):
        scripts = WidgetScript.objects.filter(region=obj)
        if scripts:
            result = ''
            n = 0
            for script in scripts:
                n += 1
                result += '{}. {}<br>'.format(n, script.name)
        else:
            result = '-'
        return mark_safe(result)

    names_script.allow_tags = True
    names_script.short_description = 'Скрипты'
