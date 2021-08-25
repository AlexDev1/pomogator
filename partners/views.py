from django.views.generic import DetailView

from partners.models import PartnerPage


class PartnerPageDetailView(DetailView):
    model = PartnerPage
    template_name = 'partners/detail.html'
