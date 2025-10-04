"""
Test factories for core app models.

Using factory_boy to create test data for core app models including
configuration models and audit models.
"""

import factory
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory

from apps.core.models import ContentConfig, SEOConfig, SiteConfig, ThemeConfig
from apps.core.sitecfg.audit_models import ConfigAudit, ConfigVersion

User = get_user_model()


class UserFactory(DjangoModelFactory):
    """Factory for creating test users."""

    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_active = True
    is_staff = False
    is_superuser = False

    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        """Set a default password for the user."""
        if not create:
            return

        password = extracted or "testpass123"
        obj.set_password(password)
        obj.save()


class StaffUserFactory(UserFactory):
    """Factory for creating staff users."""

    is_staff = True


class SuperUserFactory(UserFactory):
    """Factory for creating superusers."""

    is_staff = True
    is_superuser = True


class SiteConfigFactory(DjangoModelFactory):
    """Factory for creating SiteConfig instances."""

    class Meta:
        model = SiteConfig

    site_name = factory.Faker("company")
    site_description = factory.Faker("text", max_nb_chars=200)
    contact_email = factory.Faker("email")
    maintenance_mode = False
    timezone = "UTC"
    language_code = "en-us"


class SEOConfigFactory(DjangoModelFactory):
    """Factory for creating SEOConfig instances."""

    class Meta:
        model = SEOConfig

    default_title = factory.Faker("sentence", nb_words=4)
    default_description = factory.Faker("text", max_nb_chars=160)
    default_keywords = factory.Faker("words", nb=5, variable_nb_words=True)
    google_analytics_id = factory.Sequence(lambda n: f"GA-{n:08d}-1")
    google_site_verification = factory.Faker("sha256")
    facebook_app_id = factory.Sequence(lambda n: f"{n:15d}")
    twitter_handle = factory.Faker("user_name")


class ThemeConfigFactory(DjangoModelFactory):
    """Factory for creating ThemeConfig instances."""

    class Meta:
        model = ThemeConfig

    primary_color = "#007bff"
    secondary_color = "#6c757d"
    accent_color = "#28a745"
    success_color = "#28a745"
    warning_color = "#ffc107"
    danger_color = "#dc3545"
    info_color = "#17a2b8"
    font_family = "Inter, -apple-system, BlinkMacSystemFont, sans-serif"
    font_size_base = 16
    dark_mode_enabled = False
    custom_css = ""


class ContentConfigFactory(DjangoModelFactory):
    """Factory for creating ContentConfig instances."""

    class Meta:
        model = ContentConfig

    posts_per_page = 10
    allow_comments = True
    comment_moderation = False
    show_author_info = True
    enable_related_posts = True
    excerpt_length = 150
    date_format = "%B %d, %Y"
    enable_search = True
    enable_tags = True
    enable_categories = True


class ConfigAuditFactory(DjangoModelFactory):
    """Factory for creating ConfigAudit instances."""

    class Meta:
        model = ConfigAudit

    model_name = "SiteConfig"
    object_id = factory.Sequence(lambda n: str(n))
    action = factory.Iterator(["CREATE", "UPDATE", "DELETE"])
    old_values = factory.LazyFunction(dict)
    new_values = factory.LazyFunction(lambda: {"field": "new_value"})
    changed_fields = factory.LazyFunction(lambda: ["field"])
    user_id = None
    ip_address = factory.Faker("ipv4")
    user_agent = factory.Faker("user_agent")


class ConfigVersionFactory(DjangoModelFactory):
    """Factory for creating ConfigVersion instances."""

    class Meta:
        model = ConfigVersion

    config_type = factory.Iterator(["site", "seo", "theme", "content"])
    version_number = factory.Sequence(lambda n: n + 1)
    config_data = factory.LazyFunction(lambda: {"version": "test_data"})
    description = factory.Faker("sentence")
    created_by = factory.SubFactory(UserFactory)


# Trait mixins for common scenarios
class ConfigFactoryMixin:
    """Mixin for config-related factories."""

    @factory.trait
    def with_user(self):
        """Add a created_by user to the factory."""
        self.created_by = factory.SubFactory(UserFactory)

    @factory.trait
    def maintenance_mode(self):
        """Create config with maintenance mode enabled."""
        self.maintenance_mode = True

    @factory.trait
    def production_ready(self):
        """Create production-ready config."""
        self.maintenance_mode = False
        # Add any other production-specific settings
