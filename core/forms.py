from captcha.widgets import ReCaptchaV2Checkbox
from captcha.fields import ReCaptchaField as CaptchaField
from django import forms

class FeedbackForm(forms.Form):
    name = forms.CharField(label=u'Ваше имя')
    company = forms.CharField(label=u'Название компания')
    city = forms.CharField(label=u'Город')
    phones = forms.CharField(label=u'Телефоны')
    email = forms.EmailField(label=u'E-mail')
    phones = forms.CharField(label=u'Телефоны')
    subject = forms.CharField(label=u'Тема')
    text = forms.CharField(label=u'Ваша информация', widget=forms.Textarea())
    captcha = CaptchaField(widget=ReCaptchaV2Checkbox(attrs={'theme': 'clean'}))
    privacy = forms.BooleanField(
        label=u"""Согласен с <a href="/privacy/" target="_blank">
            политикой конфиденциальности</a>""",
        initial=True,
        required=True
    )
