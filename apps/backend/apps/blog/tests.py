from django.test import TestCase
from django.urls import reverse

from .models import BlogPost


class BlogViewsTests(TestCase):
    def setUp(self):
        self.post_draft = BlogPost.objects.create(
            title="Draft Post", body="...", status=BlogPost.DRAFT
        )
        self.post_pub = BlogPost.objects.create(
            title="Published Post",
            body="Hello",
            status=BlogPost.PUBLISHED,
        )

    def test_blog_list_shows_only_published(self):
        url = reverse("blog:list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        posts = list(resp.context["posts"])  # type: ignore[index]
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0].slug, self.post_pub.slug)

    def test_blog_detail(self):
        url = reverse("blog:detail", kwargs={"slug": self.post_pub.slug})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
