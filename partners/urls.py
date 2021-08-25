
from django.urls import path
from django.views.generic import TemplateView

from partners.views import PartnerPageDetailView

urlpatterns = [
    path('<slug:slug>/', PartnerPageDetailView.as_view(), name='partners-online'),

]
