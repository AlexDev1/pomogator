from itertools import chain

from django.conf import settings
from django.contrib import messages
from django.template.loader import render_to_string
from watson import search as watson
from django.views.generic import ListView, FormView

from core.forms import FeedbackForm
from news.models import News, Article


class SearchResultsView(ListView):
    model = News
    template_name = 'search/results.html'
    query = ''
    sort = False

    def get_queryset(self):
        query = self.request.GET.get('q', None)
        if query:
            self.query = query
            news_list = watson.filter(News, query)
            article_list = watson.filter(Article, query)
            sort = self.request.GET.get('sorted', False)
            if sort == 'true':
                self.sort = True
                result_list = list(
                    sorted(
                        chain(news_list, article_list),
                        key=lambda instance: instance.get_date_for_sorted(),
                        reverse=True)
                )
            else:
                self.sort = False
                result_list = list(
                    chain(news_list, article_list),
                )
            return result_list
        else:
            return None

    def get_context_data(self, *, object_list=None, **kwargs):
        contex = super(SearchResultsView, self).get_context_data(**kwargs)
        contex['query'] = self.query
        contex['sort'] = self.sort
        return contex


class FeedbackView(FormView):
    template_name = "feedback.html"
    form_class = FeedbackForm
    success_url = "/feedback/"

    def send_email(self, form_data):
        from django.core.mail import EmailMessage

        subject = u'Обратная связь: %s' % form_data['subject']
        body = render_to_string(
            'email/feedback.html',
            {
                'name': form_data['subject'],
                'email': form_data['email'],
                'company': form_data['company'],
                'city': form_data['city'],
                'phones': form_data['phones'],
                'subject': form_data['subject'],
                'text': form_data['text']
            }
        )

        msg = EmailMessage(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL_TITLED,
            [settings.FEEDBACK_EMAIL]
        )

        msg.content_subtype = "html"
        msg.send()

    def form_valid(self, form):
        form_valid = super(FeedbackView, self).form_valid(form)

        self.send_email(form.cleaned_data)
        messages.info(self.request, "Ваше сообщение отправлено!")

        return form_valid
