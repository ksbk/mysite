#!/usr/bin/env python3
"""
Automated Testing Demonstration Script

This script demonstrates why automated testing is superior to manual testing
by running comprehensive tests that would be tedious and error-prone to do manually.

Usage: python test_demo.py
"""

import json
import os
import sys

# Add the project to Python path
sys.path.insert(0, "/Users/ksb/dev/mysite/apps/backend")

# Set Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

import django

django.setup()

from django.test import Client  # noqa: E402

from apps.contact.models import ContactMessage  # noqa: E402


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"🧪 {title}")
    print("=" * 60)


def print_test_result(test_name, passed, details=""):
    """Print test result with emoji."""
    emoji = "✅" if passed else "❌"
    print(f"{emoji} {test_name}")
    if details:
        print(f"   📋 {details}")


def test_django_backend():
    """Test Django backend functionality automatically."""
    print_header("DJANGO BACKEND AUTOMATED TESTS")

    client = Client()
    passed_tests = 0
    total_tests = 0

    # Test 1: Contact Form GET
    total_tests += 1
    try:
        response = client.get("/contact/")
        passed = (
            response.status_code == 200 and "Contact Form" in response.content.decode()
        )
        print_test_result(
            "Contact Form Page Loads", passed, f"Status: {response.status_code}"
        )
        if passed:
            passed_tests += 1
    except Exception as e:
        print_test_result("Contact Form Page Loads", False, f"Error: {e}")

    # Test 2: AJAX API Valid Submission
    total_tests += 1
    try:
        initial_count = ContactMessage.objects.count()
        data = {
            "name": "Automated Test User",
            "email": "auto@test.com",
            "subject": "Automated Test",
            "message": "This message was created by automated testing!",
        }

        response = client.post(
            "/contact/api/",
            data=json.dumps(data),
            content_type="application/json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        response_data = json.loads(response.content) if response.content else {}
        final_count = ContactMessage.objects.count()

        passed = (
            response.status_code == 200
            and response_data.get("success")
            and final_count == initial_count + 1
        )

        print_test_result(
            "AJAX API Submission",
            passed,
            f"Messages saved: {final_count - initial_count}",
        )
        if passed:
            passed_tests += 1
    except Exception as e:
        print_test_result("AJAX API Submission", False, f"Error: {e}")

    # Test 3: Form Validation
    total_tests += 1
    try:
        invalid_data = {
            "name": "",
            "email": "invalid-email",
            "subject": "",
            "message": "Short",
        }

        response = client.post(
            "/contact/api/",
            data=json.dumps(invalid_data),
            content_type="application/json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        response_data = json.loads(response.content) if response.content else {}
        passed = (
            response.status_code == 400
            and not response_data.get("success")
            and "errors" in response_data
        )

        print_test_result("Form Validation", passed, "Correctly rejected invalid data")
        if passed:
            passed_tests += 1
    except Exception as e:
        print_test_result("Form Validation", False, f"Error: {e}")

    # Test 4: Database Integrity
    total_tests += 1
    try:
        messages = ContactMessage.objects.filter(name="Automated Test User")
        message = messages.first()

        passed = (
            message is not None
            and message.email == "auto@test.com"
            and not message.is_read
        )

        print_test_result(
            "Database Integrity", passed, f"Found {messages.count()} test messages"
        )
        if passed:
            passed_tests += 1
    except Exception as e:
        print_test_result("Database Integrity", False, f"Error: {e}")

    print(f"\n📊 Django Backend Results: {passed_tests}/{total_tests} tests passed")
    return passed_tests, total_tests


def test_manual_vs_automated():
    """Compare manual testing vs automated testing."""
    print_header("MANUAL VS AUTOMATED TESTING COMPARISON")

    print("🕐 MANUAL TESTING:")
    print("   • Open browser")
    print("   • Navigate to contact form")
    print("   • Fill out form with valid data")
    print("   • Submit and check success message")
    print("   • Go to Django admin")
    print("   • Check if message was saved")
    print("   • Test invalid data")
    print("   • Check error messages")
    print("   • Test AJAX functionality")
    print("   • Verify no page reload")
    print("   ⏱️  Time: ~5-10 minutes per test cycle")
    print("   🤔 Human error prone")
    print("   😴 Boring and repetitive")

    print("\n⚡ AUTOMATED TESTING:")
    print("   • Run: python test_demo.py")
    print("   ⏱️  Time: ~2-3 seconds")
    print("   🎯 100% consistent")
    print("   🔄 Can run thousands of times")
    print("   📈 Tests more scenarios than humanly possible")
    print("   🐛 Catches regressions immediately")


def test_scenarios_humans_miss():
    """Test edge cases that humans often miss."""
    print_header("EDGE CASES HUMANS OFTEN MISS")

    client = Client()
    edge_cases = [
        {
            "name": "Unicode Test 🚀",
            "email": "unicode@test.com",
            "subject": "Testing Unicode: 日本語",
            "message": "This tests unicode handling: ñáéíóú 中文 العربية",
        },
        {
            "name": "A" * 100,  # Max length test
            "email": "long@test.com",
            "subject": "Long Name Test",
            "message": "Testing maximum name length boundaries.",
        },
        {
            "name": "SQL Injection Test",
            "email": "sql@test.com",
            "subject": "'; DROP TABLE contact_contactmessage; --",
            "message": "Testing SQL injection protection.",
        },
    ]

    for i, test_data in enumerate(edge_cases, 1):
        try:
            response = client.post(
                "/contact/api/",
                data=json.dumps(test_data),
                content_type="application/json",
                HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            )

            passed = response.status_code in [
                200,
                400,
            ]  # Either success or validation error
            print_test_result(
                f"Edge Case {i}: {test_data["subject"][:30]}...",
                passed,
                "Handled gracefully",
            )
        except Exception as e:
            print_test_result(f"Edge Case {i}", False, f"Error: {e}")


def main():
    """Run the complete testing demonstration."""
    print("🎯 AUTOMATED TESTING DEMONSTRATION")
    print("This script shows why automated testing is essential!")

    # Run Django tests
    django_passed, django_total = test_django_backend()

    # Show comparison
    test_manual_vs_automated()

    # Test edge cases
    test_scenarios_humans_miss()

    # Final summary
    print_header("SUMMARY: WHY AUTOMATED TESTING WINS")
    print("✅ Speed: Tests run in seconds, not minutes")
    print("✅ Reliability: Same results every time")
    print("✅ Coverage: Tests edge cases humans forget")
    print("✅ Regression Detection: Catches breaking changes")
    print("✅ Documentation: Tests show how code should work")
    print("✅ Confidence: Deploy with confidence")

    print(f"\n🎉 Total Backend Tests: {django_passed}/{django_total} passed")

    if django_passed == django_total:
        print("🌟 All tests passed! Your contact form is solid!")
    else:
        print("⚠️  Some tests failed. Use this to debug and improve!")


if __name__ == "__main__":
    main()
