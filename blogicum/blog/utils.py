from django.utils import timezone

from blog.models import Post


def get_post_list():
    """Список объектов Post."""
    return Post.objects.select_related(
        'author', 'location', 'category'
    ).filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    )
