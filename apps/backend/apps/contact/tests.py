from django.test import TestCase
from django.urls import reverse

from .models import ContactMessage


class ContactViewTests(TestCase):
    def test_get_contact_form(self):
        url = reverse("contact:form")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_submit_contact_form(self):
        url = reverse("contact:form")
        data = {
            "name": "Jane",
            "email": "jane@example.com",
            "subject": "Hello",
            "message": "Testing",
        }
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(
            ContactMessage.objects.filter(email="jane@example.com").exists()
        )
