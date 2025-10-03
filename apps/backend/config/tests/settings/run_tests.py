"""Test configuration and runner for Django settings tests."""

import os
import sys

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Set Django settings module for tests
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.test")

import django
from django.conf import settings
from django.test.utils import get_runner


def run_settings_tests():
    """Run all settings-related tests."""
    django.setup()

    test_modules = [
        "config.settings.tests.test_env_validation",
        "config.settings.tests.test_django_settings",
        "config.settings.tests.test_environment_settings",
        "config.settings.tests.test_request_id",
    ]

    TestRunner = get_runner(settings)
    test_runner = TestRunner()

    failures = test_runner.run_tests(test_modules)

    if failures:
        sys.exit(1)
    else:
        print("All settings tests passed!")


if __name__ == "__main__":
    run_settings_tests()
