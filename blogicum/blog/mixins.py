from django.db.models import Count

from blog.models import Comment, Post
from blog.utils import get_post_list

NUM_POSTS = 10


class PostMixin:
    model = Post
    paginate_by = NUM_POSTS

    def get_queryset(self):
        return get_post_list().annotate(
            comment_count=(Count('comments'))).order_by('-pub_date')


class CommentMixin:
    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def get_queryset(self):
        return Comment.objects.filter(author=self.request.user)
