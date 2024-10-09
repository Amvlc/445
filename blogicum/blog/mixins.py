from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from .models import Comment, Post
from .utils import get_post_queryset
from .const import PAGINATE_BY


class PostListMixin:
    model = Post
    paginate_by = PAGINATE_BY

    def get_queryset(self):
        return get_post_queryset(
            self.model.objects.all(),
            filter_published=True,
            annotate_comments=True,
        )


class AuthorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user


class CommentMixin:
    model = Comment

    def get_object(self):
        return get_object_or_404(
            self.model,
            id=self.kwargs["comment_id"],
            post_id=self.kwargs["post_id"],
        )

    def get_success_url(self):
        return reverse(
            "blog:post_detail", kwargs={"post_id": self.kwargs["post_id"]}
        )
