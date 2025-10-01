#!/usr/bin/env python
"""
V1 Ship Validation Script

Run this script to validate that v1 is ready for production deployment.
This checks all the critical v1 requirements.
"""

import django
import os
import sys

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
django.setup()

from django.core.management import call_command

from apps.core.config import ConfigService


def validate_v1_readiness():
    """Validate v1 is ready to ship."""

    print("🚀 V1 SHIPMENT VALIDATION")
    print("=" * 50)

    checks = []

    # 1. Check Django system
    print("✓ Checking Django system...")
    try:
        call_command("check", verbosity=0)
        checks.append(("Django system check", True, "All checks passed"))
    except Exception as e:
        checks.append(("Django system check", False, str(e)))

    # 2. Check configuration system
    print("✓ Checking configuration system...")
    try:
        config = ConfigService.get_config()
        required_sections = ["site", "seo", "theme", "content"]
        missing = [s for s in required_sections if s not in config]
        if missing:
            checks.append(("Config system", False, f"Missing sections: {missing}"))
        else:
            checks.append(("Config system", True, "All sections present"))
    except Exception as e:
        checks.append(("Config system", False, str(e)))

    # 3. Check cache functionality
    print("✓ Checking cache functionality...")
    try:
        from apps.core.config.cache import cache_manager

        test_key = cache_manager.get_site_config_key()
        cache_manager.set(test_key, {"test": True})
        cached_data = cache_manager.get(test_key)
        if cached_data and cached_data.get("test"):
            checks.append(("Cache system", True, "Cache read/write working"))
        else:
            checks.append(("Cache system", False, "Cache not working properly"))
        cache_manager.delete(test_key)
    except Exception as e:
        checks.append(("Cache system", False, str(e)))

    # 4. Check template system
    print("✓ Checking template system...")
    try:
        from django.template.loader import get_template

        base_template = get_template("core/base.html")
        error_template = get_template("404.html")
        checks.append(("Template system", True, "Templates loading correctly"))
    except Exception as e:
        checks.append(("Template system", False, str(e)))

    # 5. Check middleware
    print("✓ Checking middleware...")
    try:
        from apps.core.middleware.csp import CSPNonceMiddleware
        from apps.core.middleware.feature_flags import FeatureFlagMiddleware

        checks.append(("Middleware", True, "Middleware classes importable"))
    except Exception as e:
        checks.append(("Middleware", False, str(e)))

    # 6. Check management commands
    print("✓ Checking management commands...")
    try:
        from django.core.management import get_commands

        commands = get_commands()
        required_commands = [
            "init_config",
            "export_config",
            "validate_config",
            "qa_check",
        ]
        missing_commands = [cmd for cmd in required_commands if cmd not in commands]
        if missing_commands:
            checks.append((
                "Management commands",
                False,
                f"Missing: {missing_commands}",
            ))
        else:
            checks.append(("Management commands", True, "All commands available"))
    except Exception as e:
        checks.append(("Management commands", False, str(e)))

    # Print results
    print("\n" + "=" * 50)
    print("VALIDATION RESULTS")
    print("=" * 50)

    all_passed = True
    for name, passed, message in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {name}: {message}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 50)

    if all_passed:
        print("🎉 V1 IS READY TO SHIP!")
        print("\nNext steps for production deployment:")
        print("1. Apply production settings from PRODUCTION_SETTINGS.py")
        print("2. Set up Redis cache")
        print("3. Configure PostgreSQL database")
        print("4. Set up SSL/HTTPS")
        print("5. Run migrations: python manage.py migrate")
        print("6. Create superuser: python manage.py createsuperuser")
        print("7. Initialize config: python manage.py init_config")
        print("8. Collect static files: python manage.py collectstatic")
        print("9. Run final QA check: python manage.py qa_check")
        return True
    else:
        print("❌ V1 NOT READY - Fix the issues above first")
        return False


if __name__ == "__main__":
    success = validate_v1_readiness()
    sys.exit(0 if success else 1)
