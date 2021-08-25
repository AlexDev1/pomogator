from django import template

from banner.models import WidgetRegion

register = template.Library()


@register.inclusion_tag('widgets/widget_brending.html', takes_context=True)
def get_widget_branding(context):
    """ Тег готорый возвращает скрипт виджетов
    :return: template to widgets
    """
    try:
        regions = WidgetRegion.objects.filter(section=0, active=True)
    except:
        return None

    if regions:
        context['script_branding_list'] = regions
        return context
    else:
        return None


@register.inclusion_tag('widgets/widget_script.html', takes_context=True)
def get_widget_scripts(context, section):
    """
    Тег готорый возвращает скрипт виджетов
    :return: template to widgets
    """
    # if section:
    try:
        regions = WidgetRegion.objects.filter(section=section, active=True)
    except:
        return None
    context['scripts_list'] = regions
    return context
