from django.views.generic import DetailView, ListView

from .models import BlogPost


class BlogListView(ListView):
    model = BlogPost
    template_name = "blog/list.html"
    context_object_name = "posts"

    def get_queryset(self):
        return (
            BlogPost.objects.filter(status=BlogPost.PUBLISHED)
            .order_by("-published_at", "-created_at")
            .all()
        )


class BlogDetailView(DetailView):
    model = BlogPost
    template_name = "blog/detail.html"
    context_object_name = "post"
    slug_field = "slug"
    slug_url_kwarg = "slug"
