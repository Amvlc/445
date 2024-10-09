from django.db.models import Count, Q
from django.utils import timezone

from .models import Post


def get_post_queryset(
    manager=Post.objects, filter_published=True, annotate_comments=True
):
    queryset = manager.select_related()
    if filter_published:
        queryset = queryset.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now(),
        )
    if annotate_comments:
        queryset = queryset.annotate(
            comment_count=Count(
                "comments", filter=Q(comments__is_published=True)
            )
        ).order_by("-pub_date")
    return queryset
