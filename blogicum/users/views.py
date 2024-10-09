from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    PasswordChangeDoneView,
    PasswordChangeView,
)

from django.urls import reverse_lazy


User = get_user_model()


class ChangePasswordView(LoginRequiredMixin, PasswordChangeView):
    template_name = "users/password_change.html"
    success_url = reverse_lazy("users:password_change_done")


class ChangePasswordDoneView(LoginRequiredMixin, PasswordChangeDoneView):
    template_name = "users/password_change_done.html"
