from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from blog.forms import CommentForm, PostForm
from blog.mixins import CommentMixin, PostMixin
from blog.models import Category, Comment, Post, User
from blog.utils import get_post_list


class PostListView(PostMixin, ListView):
    """Страница списка постов."""

    template_name = 'blog/index.html'


class PostDetailView(DetailView):
    """Страница поста."""

    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/detail.html'

    def get_object(self, queryset=None):
        post = get_object_or_404(
            Post.objects.select_related(
                'author', 'location', 'category'
            ),
            pk=self.kwargs['post_id']
        )
        if post.author == self.request.user:
            return post
        return get_object_or_404(
            get_post_list(),
            pk=self.kwargs['post_id']
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context


class CategoryPostsListView(PostMixin, ListView):
    """Страница списка категорий поста."""

    model = Category
    slug_url_kwarg = 'category_slug'
    template_name = 'blog/category.html'

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return super().get_queryset().filter(category=self.category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class ProfileListView(PostMixin, ListView):
    """Страница профиля."""

    slug_url_kwarg = 'username'
    template_name = 'blog/profile.html'

    def get_queryset(self):
        self.author = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
        if self.author != self.request.user:
            return super().get_queryset()
        return Post.objects.select_related(
            'author', 'location', 'category').filter(author=self.author)

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


class PostUpdateView(LoginRequiredMixin, UpdateView):
    """Страница редактирования поста."""

    model = Post
    form_class = PostForm
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect('blog:post_detail', kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


@login_required
def post_delete(request, post_id):
    """Страница удаления поста."""
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(instance=post)
    context = {'form': form}
    if request.method == 'POST':
        if post.author == request.user:
            post.delete()
        return redirect('blog:index')
    return render(request, 'blog/create.html', context)


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Страница создания комментария поста."""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(
            Post,
            pk=self.kwargs['post_id']
        )
        return super().form_valid(form)


class CommentUpdateView(CommentMixin, LoginRequiredMixin, UpdateView):
    """Страница редактирования комментария поста."""

    form_class = CommentForm


class CommentDeleteView(CommentMixin, LoginRequiredMixin, DeleteView):
    """Страница удаления комментария поста."""

    success_url = reverse_lazy('blog:index')
