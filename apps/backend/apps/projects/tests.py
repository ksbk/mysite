from django.test import TestCase
from django.urls import reverse

from .models import Project


class ProjectViewsTests(TestCase):
    def setUp(self):
        self.project = Project.objects.create(name="Alpha")

    def test_projects_list(self):
        url = reverse("projects:list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        projects = list(resp.context["projects"])  # type: ignore[index]
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0].slug, self.project.slug)

    def test_projects_detail(self):
        url = reverse("projects:detail", kwargs={"slug": self.project.slug})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
