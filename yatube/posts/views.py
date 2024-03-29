from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post
from .utils import paginate_posts

User = get_user_model()


@cache_page(20, key_prefix='index_page')
def index(request):
    """Главная страница."""
    page_obj = paginate_posts(request, Post.objects.select_related())
    context = {'page_obj': page_obj, }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Страница группы."""
    group = get_object_or_404(Group, slug=slug)
    page_obj = paginate_posts(
        request,
        group.posts.select_related('author'))
    context = {
        'page_obj': page_obj,
        'group': group,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    page_obj = paginate_posts(request, author.posts.select_related())
    num_posts = author.posts.count()
    following = request.user.is_authenticated and author.following.filter(
        user=request.user
    ).exists()

    context = {
        'page_obj': page_obj,
        'author': author,
        'num_posts': num_posts,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    num_posts = post.author.posts.count()
    is_author = bool(post.author == request.user)
    form = CommentForm(request.POST or None)
    comments = post.comments.select_related()
    num_comments = post.comments.count()
    context = {
        'post': post,
        'num_posts': num_posts,
        'is_author': is_author,
        'form': form,
        'comments': comments,
        'num_comments': num_comments,
    }

    return render(
        request, 'posts/post_detail.html', context
    )


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )

    if form.is_valid():
        form_data = form.save(commit=False)
        form_data.author = request.user
        form_data.save()

        return redirect('posts:profile', request.user.username)

    context = {
        'form': form,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if post.author != request.user:
        return redirect('posts:post_detail', post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)

    context = {
        'is_edit': True,
        'form': form,
        'post_id': post_id,
    }

    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = Post.objects.get(pk=post_id)
        comment.save()

    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(
        author__following__user=request.user
    ).select_related()
    page_obj = paginate_posts(request, posts)

    context = {'page_obj': page_obj}

    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user and not request.user.follower.filter(
        author=author
    ).exists():
        Follow.objects.create(user=request.user, author=author)

    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follow = request.user.follower.filter(author=author)
    if follow.exists():
        follow.delete()

    return redirect('posts:follow_index')
