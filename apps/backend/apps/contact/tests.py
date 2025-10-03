"""
Comprehensive tests for the Contact app - both traditional forms and AJAX API.

Tests cover:
1. Model validation and database operations
2. Form validation and cleaning
3. Traditional form view functionality
4. AJAX API endpoints
5. Error handling and edge cases
"""

import json

from django.test import Client, TestCase
from django.urls import reverse

from .forms import ContactForm
from .models import ContactMessage


class ContactMessageModelTest(TestCase):
    """Test the ContactMessage model validation and database operations."""

    def test_create_valid_contact_message(self):
        """Test creating a valid contact message."""
        message = ContactMessage.objects.create(
            name="John Doe",
            email="john@example.com",
            subject="Test Subject",
            message="This is a test message with enough characters to pass validation.",
        )

        self.assertEqual(message.name, "John Doe")
        self.assertEqual(message.email, "john@example.com")
        self.assertEqual(message.subject, "Test Subject")
        self.assertTrue(len(message.message) > 10)
        self.assertFalse(message.is_read)
        self.assertIsNotNone(message.created_at)

    def test_contact_message_str_representation(self):
        """Test the string representation of ContactMessage."""
        message = ContactMessage(name="Jane Smith", subject="Test Subject")
        # String includes date, so we test the pattern
        expected_pattern = "Jane Smith - Test Subject (20"
        self.assertTrue(str(message).startswith(expected_pattern))

    def test_contact_message_ordering(self):
        """Test that messages are ordered by creation date (newest first)."""
        # Create messages in specific order
        msg1 = ContactMessage.objects.create(
            name="First",
            email="first@test.com",
            subject="First",
            message="First message content here.",
        )
        msg2 = ContactMessage.objects.create(
            name="Second",
            email="second@test.com",
            subject="Second",
            message="Second message content here.",
        )

        messages = ContactMessage.objects.all()
        self.assertEqual(messages[0], msg2)  # Newest first
        self.assertEqual(messages[1], msg1)


class ContactFormTest(TestCase):
    """Test the ContactForm validation and cleaning methods."""

    def test_valid_form_data(self):
        """Test form with valid data."""
        form_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "subject": "Test Subject",
            "message": "This is a detailed test message with sufficient length.",
        }
        form = ContactForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_missing_required_fields(self):
        """Test form validation with missing required fields."""
        form_data = {}
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())

        # Check that all required fields have errors
        self.assertIn("name", form.errors)
        self.assertIn("email", form.errors)
        self.assertIn("subject", form.errors)
        self.assertIn("message", form.errors)

    def test_form_email_validation(self):
        """Test email field validation."""
        # Invalid email
        form_data = {
            "name": "John Doe",
            "email": "invalid-email",
            "subject": "Test",
            "message": "Test message content here.",
        }
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_form_message_length_validation(self):
        """Test custom message length validation."""
        # Message too short
        form_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "subject": "Test",
            "message": "Short",  # Less than 10 characters
        }
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("message", form.errors)
        self.assertIn("at least 10 characters", str(form.errors["message"]))


class ContactFormViewTest(TestCase):
    """Test the traditional contact form view (non-AJAX)."""

    def setUp(self):
        self.client = Client()
        self.form_url = reverse("contact:form")
        self.success_url = reverse("contact:success")

    def test_contact_form_get(self):
        """Test GET request to contact form."""
        response = self.client.get(self.form_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Contact Form")
        self.assertIsInstance(response.context["form"], ContactForm)

    def test_contact_form_post_valid(self):
        """Test POST request with valid form data."""
        form_data = {
            "name": "Test User",
            "email": "test@example.com",
            "subject": "Test Subject",
            "message": "This is a test message with sufficient length for validation.",
        }

        response = self.client.post(self.form_url, form_data)

        # Should redirect to success page
        self.assertRedirects(response, self.success_url)

        # Check that message was saved to database
        self.assertEqual(ContactMessage.objects.count(), 1)
        message = ContactMessage.objects.first()
        self.assertEqual(message.name, "Test User")
        self.assertEqual(message.email, "test@example.com")

    def test_contact_form_post_invalid(self):
        """Test POST request with invalid form data."""
        form_data = {
            "name": "",  # Missing required field
            "email": "invalid-email",
            "subject": "",
            "message": "Short",  # Too short
        }

        response = self.client.post(self.form_url, form_data)

        # Should not redirect, should show form with errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required")

        # No message should be saved
        self.assertEqual(ContactMessage.objects.count(), 0)


class ContactAPIViewTest(TestCase):
    """Test the AJAX API endpoint for contact form submission."""

    def setUp(self):
        self.client = Client()
        self.api_url = reverse("contact:api")

    def test_api_post_valid_json(self):
        """Test AJAX API with valid JSON data."""
        data = {
            "name": "AJAX User",
            "email": "ajax@example.com",
            "subject": "AJAX Test",
            "message": "This is an AJAX test message with sufficient length.",
        }

        response = self.client.post(
            self.api_url,
            data=json.dumps(data),
            content_type="application/json",
            headers={"x-requested-with": "XMLHttpRequest"}
        )

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)

        # Check response structure
        self.assertTrue(response_data["success"])
        self.assertIn("Thanks AJAX User", response_data["message"])

        # Check database save
        self.assertEqual(ContactMessage.objects.count(), 1)
        message = ContactMessage.objects.first()
        self.assertEqual(message.name, "AJAX User")

    def test_api_post_invalid_json(self):
        """Test AJAX API with invalid JSON data."""
        data = {
            "name": "",  # Missing required field
            "email": "invalid-email",
            "subject": "",
            "message": "Short",  # Too short
        }

        response = self.client.post(
            self.api_url,
            data=json.dumps(data),
            content_type="application/json",
            headers={"x-requested-with": "XMLHttpRequest"}
        )

        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)

        # Check error response structure
        self.assertFalse(response_data["success"])
        self.assertIn("errors", response_data)
        self.assertIn("name", response_data["errors"])
        self.assertIn("email", response_data["errors"])
        self.assertIn("message", response_data["errors"])

        # No message should be saved
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_api_get_requests(self):
        """Test that GET requests to API endpoint return form schema."""
        response = self.client.get(self.api_url)
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content)
        # API should return form field information
        self.assertIn("fields", response_data)
        self.assertIn("name", response_data["fields"])
        self.assertIn("email", response_data["fields"])
        self.assertIn("subject", response_data["fields"])
        self.assertIn("message", response_data["fields"])

    def test_api_post_non_ajax(self):
        """Test API endpoint with non-AJAX POST (should still work)."""
        data = {
            "name": "Regular User",
            "email": "regular@example.com",
            "subject": "Regular Test",
            "message": "This is a regular POST test message.",
        }

        response = self.client.post(self.api_url, data)

        # Should work but return different format
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data["success"])


class ContactIntegrationTest(TestCase):
    """Integration tests for the complete contact form workflow."""

    def test_full_ajax_workflow(self):
        """Test the complete AJAX submission workflow."""
        # 1. Get the form page
        form_url = reverse("contact:form")
        response = self.client.get(form_url)
        self.assertEqual(response.status_code, 200)

        # 2. Submit via AJAX API
        api_url = reverse("contact:api")
        data = {
            "name": "Integration Test User",
            "email": "integration@example.com",
            "subject": "Integration Test",
            "message": "Integration test message to verify complete workflow.",
        }

        response = self.client.post(
            api_url,
            data=json.dumps(data),
            content_type="application/json",
            headers={"x-requested-with": "XMLHttpRequest"}
        )

        # 3. Verify API response
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data["success"])

        # 4. Verify database state
        self.assertEqual(ContactMessage.objects.count(), 1)
        message = ContactMessage.objects.first()
        self.assertEqual(message.name, "Integration Test User")
        self.assertEqual(message.email, "integration@example.com")
        self.assertFalse(message.is_read)

        # 5. Verify we can still access traditional success page
        success_url = reverse("contact:success")
        response = self.client.get(success_url)
        self.assertEqual(response.status_code, 200)

    def test_form_fallback_workflow(self):
        """Test traditional form submission as fallback."""
        form_url = reverse("contact:form")
        data = {
            "name": "Traditional User",
            "email": "traditional@example.com",
            "subject": "Traditional Test",
            "message": "This is a traditional form submission test message.",
        }

        response = self.client.post(form_url, data)

        # Should redirect to success page
        success_url = reverse("contact:success")
        self.assertRedirects(response, success_url)

        # Should save to database
        self.assertEqual(ContactMessage.objects.count(), 1)


class ContactMessageAdminTest(TestCase):
    """Test admin interface functionality for ContactMessage."""

    def test_message_admin_display(self):
        """Test that messages display properly in admin."""
        message = ContactMessage.objects.create(
            name="Admin Test User",
            email="admin@example.com",
            subject="Admin Test",
            message="This is an admin test message.",
        )

        # Test string representation (used in admin)
        expected_pattern = "Admin Test User - Admin Test (20"
        self.assertTrue(str(message).startswith(expected_pattern))

        # Test that admin fields are accessible
        self.assertIsNotNone(message.created_at)
        self.assertFalse(message.is_read)
