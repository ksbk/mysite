"""
Test factories for pages app models.

Using factory_boy to create test data for pages app models.
This is a placeholder for when page models are created.
"""

from django.contrib.auth import get_user_model

User = get_user_model()


# Placeholder factories for future page models
# Uncomment and modify when page models are created

# class PageFactory(DjangoModelFactory):
#     """Factory for creating Page instances."""
#
#     class Meta:
#         model = Page  # from apps.pages.models import Page
#
#     title = factory.Faker('sentence', nb_words=4)
#     slug = factory.LazyAttribute(lambda obj: obj.title.lower().replace(' ', '-'))
#     content = factory.Faker('text', max_nb_chars=1000)
#     excerpt = factory.LazyAttribute(lambda obj: obj.content[:150] + '...')
#     is_published = True
#     author = factory.SubFactory('apps.core.tests.factories.UserFactory')
#     created_at = factory.Faker('date_time_this_year')
#     updated_at = factory.LazyAttribute(lambda obj: obj.created_at)
#
#     @factory.trait
#     def draft(self):
#         """Create unpublished page."""
#         is_published = False
#
#     @factory.trait
#     def with_custom_slug(self):
#         """Create page with custom slug."""
#         slug = factory.Faker('slug')


# class CategoryFactory(DjangoModelFactory):
#     """Factory for creating Category instances."""
#
#     class Meta:
#         model = Category  # from apps.pages.models import Category
#
#     name = factory.Faker('word')
#     slug = factory.LazyAttribute(lambda obj: obj.name.lower().replace(' ', '-'))
#     description = factory.Faker('sentence')
#
#     @factory.trait
#     def with_parent(self):
#         """Create category with parent."""
#         parent = factory.SubFactory(CategoryFactory)


# Helper function for creating test data
def create_sample_pages(count=5):
    """Create sample pages for testing."""
    # return PageFactory.create_batch(count)
    pass  # Placeholder until Page model exists


def create_pages_with_categories(page_count=3, category_count=2):
    """Create pages with associated categories."""
    # categories = CategoryFactory.create_batch(category_count)
    # pages = []
    # for i in range(page_count):
    #     page = PageFactory.create()
    #     page.categories.set(categories[:2])  # Assign first 2 categories
    #     pages.append(page)
    # return pages, categories
    pass  # Placeholder until models exist
