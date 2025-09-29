from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from .models import ContactMessage


class ContactView(CreateView):
    model = ContactMessage
    template_name = "contact/contact.html"
    fields = ["name", "email", "subject", "message"]
    success_url = reverse_lazy("contact:success")

    def form_valid(self, form):
        messages.success(self.request, "Thanks! Your message has been sent.")
        return super().form_valid(form)


class ContactSuccessView(TemplateView):
    template_name = "contact/success.html"
