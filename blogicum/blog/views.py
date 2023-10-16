from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from blog.forms import CommentForm, PostForm
from blog.models import Category, Comment, Post


NUM_POSTS = 10
User = get_user_model()


def get_post_list():
    """Список объектов Post."""
    return Post.objects.select_related(
        'author', 'location', 'category'
    ).filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    )


class PostListView(ListView):
    """Страница списка постов."""

    model = Post
    queryset = get_post_list().annotate(
        comment_count=(Count('comments'))).order_by('-pub_date')
    paginate_by = NUM_POSTS
    template_name = 'blog/index.html'


class PostDetailView(DetailView):
    """Страница поста."""

    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/detail.html'

    def get_object(self, queryset=None):
        instance = get_object_or_404(
            Post,
            pk=self.kwargs['post_id']
        )
        if instance.author == self.request.user:
            return instance
        else:
            return get_object_or_404(
                get_post_list(),
                pk=self.kwargs['post_id']
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context


class CategoryPostsListView(ListView):
    """Страница списка категорий поста."""

    model = Category
    paginate_by = NUM_POSTS
    slug_url_kwarg = 'category_slug'
    template_name = 'blog/category.html'

    def get_queryset(self):
        return get_post_list().filter(
            category__slug=self.kwargs['category_slug']
        ).annotate(comment_count=Count('comments')).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return context


class ProfileListView(ListView):
    """Страница профиля."""

    model = Post
    paginate_by = NUM_POSTS
    slug_url_kwarg = 'username'
    template_name = 'blog/profile.html'

    def get_queryset(self):
        self.author = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
        return Post.objects.select_related(
            'author', 'location', 'category'
        ).filter(author=self.author).order_by(
            '-pub_date'
        ).annotate(comment_count=Count('comments'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.author
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Страница редактирования профиля."""

    fields = ('first_name', 'last_name', 'username', 'email')
    template_name = 'blog/user.html'
    success_url = reverse_lazy('blog:index')

    def get_object(self, queryset=None):
        return self.request.user


class PostCreateView(LoginRequiredMixin, CreateView):
    """Страница создания поста."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile', args=[self.request.user])


class PostUpdateView(UpdateView):
    """Страница редактирования поста."""

    model = Post
    form_class = PostForm
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(
            Post,
            pk=kwargs['post_id'],
        )
        if instance.author != request.user:
            return redirect('blog:post_detail', kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


@login_required
def post_delete(request, post_id):
    """Страница удаления поста."""
    instance = get_object_or_404(Post, pk=post_id)
    form = PostForm(instance=instance)
    context = {'form': form}
    if request.method == 'POST':
        if instance.author == request.user:
            instance.delete()
        return redirect('blog:index')
    return render(request, 'blog/create.html', context)


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Страница создания комментария поста."""

    post_object = None
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        self.post_object = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_object
        return super().form_valid(form)


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    """Страница редактирования комментария поста."""

    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def get_queryset(self):
        return Comment.objects.filter(author=self.request.user)


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    """Страница удаления комментария поста."""

    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'
    success_url = reverse_lazy('blog:index')

    def get_queryset(self):
        return Comment.objects.filter(author=self.request.user)