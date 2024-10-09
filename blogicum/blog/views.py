from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import CommentForm, EditProfileForm, PostForm
from .mixins import PostListMixin, CommentMixin, AuthorRequiredMixin
from .models import Comment, Category, Post, User
from .query_utils import get_post_queryset
from django.conf import settings

User = get_user_model()


class PostListView(PostListMixin, ListView):
    template_name = "blog/index.html"


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/detail.html"

    def get_object(self, queryset=None):
        filter_published = self.request.user != self.object.author
        return get_object_or_404(
            get_post_queryset(
                filter_published=filter_published,
                annotate_comments=False,
            ),
            pk=self.kwargs["post_id"],
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comments"] = self.object.comments.filter(
            is_published=True
        ).select_related("author")
        context["form"] = CommentForm()
        return context


class CategoryPostListView(ListView):
    template_name = "blog/category.html"
    paginate_by = settings.PAGINATE_BY

    def get_queryset(self):
        category = get_object_or_404(
            Category, slug=self.kwargs["category_slug"], is_published=True
        )
        return get_post_queryset(
            manager=category.posts,
            filter_published=True,
            annotate_comments=True,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = get_object_or_404(
            Category, slug=self.kwargs["category_slug"], is_published=True
        )
        context["category"] = category
        return context


class CreatePostView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "blog/create.html"

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        post.save()
        return redirect("blog:profile", username=self.request.user.username)


class EditPostView(LoginRequiredMixin, AuthorRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blog/create.html"
    pk_url_kwarg = "post_id"

    def handle_no_permission(self):
        return redirect("blog:post_detail", post_id=self.kwargs["post_id"])


class DeletePostView(LoginRequiredMixin, AuthorRequiredMixin, DeleteView):
    model = Post
    template_name = "blog/delete.html"
    pk_url_kwarg = "post_id"

    def get_success_url(self):
        return reverse(
            "blog:profile", kwargs={"username": self.request.user.username}
        )


class ProfileView(ListView):
    template_name = "blog/profile.html"
    paginate_by = settings.PAGINATE_BY

    def get_user(self):
        return get_object_or_404(User, username=self.kwargs["username"])

    def get_queryset(self):
        user = self.get_user()
        return get_post_queryset(
            manager=user.posts,
            filter_published=self.request.user != user,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_user()
        context["profile"] = user
        return context


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = EditProfileForm
    template_name = "blog/user.html"

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse(
            "blog:profile", kwargs={"username": self.request.user.username}
        )


class AddCommentView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = "blog/detail.html"

    def form_valid(self, form):
        post = get_object_or_404(Post, id=self.kwargs["post_id"])
        comment = form.save(commit=False)
        comment.post = post
        comment.author = self.request.user
        comment.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "blog:post_detail", kwargs={"post_id": self.kwargs["post_id"]}
        )


class EditCommentView(
    LoginRequiredMixin, AuthorRequiredMixin, CommentMixin, UpdateView
):
    form_class = CommentForm
    template_name = "blog/create.html"


class DeleteCommentView(
    LoginRequiredMixin, AuthorRequiredMixin, CommentMixin, DeleteView
):
    template_name = "blog/comment.html"
