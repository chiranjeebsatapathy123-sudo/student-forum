from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Post, Comment, Category
from .forms import UserRegisterForm, PostForm, CommentForm, CategoryForm, UserUpdateForm
from .utils import apply_bootstrap_classes


def home(request):
    query = request.GET.get("q", "")
    category_id = request.GET.get("category", "")
    posts = Post.objects.all()

    if query:
        posts = posts.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if category_id:
        posts = posts.filter(category_id=category_id)

    paginator = Paginator(posts, 6)
    page = request.GET.get("page")
    posts = paginator.get_page(page)

    categories = Category.objects.all()
    return render(
        request,
        "studentforum/home.html",
        {
            "posts": posts,
            "categories": categories,
            "query": query,
            "selected_category": category_id,
        },
    )


def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.username}! Your account has been created.")
            return redirect("dashboard")
    else:
        form = UserRegisterForm()
    return render(request, "studentforum/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        apply_bootstrap_classes(form)
        if "username" in form.fields:
            form.fields["username"].widget.attrs["autofocus"] = True
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect(request.GET.get("next", "dashboard"))
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
        apply_bootstrap_classes(form)
        if "username" in form.fields:
            form.fields["username"].widget.attrs["autofocus"] = True
    return render(request, "studentforum/login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("home")


@login_required
def dashboard(request):
    user_posts = Post.objects.filter(user=request.user).order_by("-created_date")
    user_comments = Comment.objects.filter(user=request.user).order_by("-created_date")
    return render(
        request,
        "studentforum/dashboard.html",
        {
            "user_posts": user_posts,
            "user_comments": user_comments,
            "recent_posts": user_posts[:5],
            "recent_comments": user_comments[:5],
            "total_posts": user_posts.count(),
            "total_comments": user_comments.count(),
        },
    )


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("dashboard")
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, "studentforum/edit_profile.html", {"form": form})


@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password changed successfully!")
            return redirect("dashboard")

    else:
        form = PasswordChangeForm(request.user)
    apply_bootstrap_classes(form)
    return render(request, "studentforum/change_password.html", {"form": form})


@login_required
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            messages.success(request, "Post created successfully!")
            return redirect("post_detail", pk=post.pk)
    else:
        form = PostForm()
    return render(request, "studentforum/create_post.html", {"form": form, "title": "Create Post"})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.all()
    comment_form = CommentForm()

    if request.method == "POST" and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.user = request.user

            comment.save()
            messages.success(request, "Comment added!")
            return redirect("post_detail", pk=pk)

    return render(
        request,
        "studentforum/post_detail.html",
        {
            "post": post,
            "comments": comments,
            "comment_form": comment_form,
        },
    )


@login_required
def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.user != request.user and not request.user.is_staff:
        messages.error(request, "You are not authorized to edit this post.")
        return redirect("post_detail", pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post updated successfully!")
            return redirect("post_detail", pk=pk)
    else:
        form = PostForm(instance=post)
    return render(request, "studentforum/create_post.html", {"form": form, "title": "Edit Post", "post": post})


@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.user != request.user and not request.user.is_staff:
        messages.error(request, "You are not authorized to delete this post.")
        return redirect("post_detail", pk=pk)
    if request.method == "POST":
        post.delete()
        messages.success(request, "Post deleted successfully!")
        return redirect("home")
    return render(request, "studentforum/confirm_delete.html", {"object": post, "type": "Post"})


@login_required
def edit_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if comment.user != request.user and not request.user.is_staff:
        messages.error(request, "Not authorized.")
        return redirect("post_detail", pk=comment.post.pk)
    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, "Comment updated!")
            return redirect("post_detail", pk=comment.post.pk)
    else:
        form = CommentForm(instance=comment)
    return render(request, "studentforum/edit_comment.html", {"form": form, "comment": comment})


@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post_pk = comment.post.pk
    if comment.user != request.user and not request.user.is_staff:
        messages.error(request, "Not authorized.")
        return redirect("post_detail", pk=post_pk)
    if request.method == "POST":
        comment.delete()
        messages.success(request, "Comment deleted!")
        return redirect("post_detail", pk=post_pk)
    return render(request, "studentforum/confirm_delete.html", {"object": comment, "type": "Comment"})


def category_list(request):
    categories = Category.objects.all()

    return render(request, "studentforum/category_list.html", {"categories": categories})


def category_posts(request, pk):
    category = get_object_or_404(Category, pk=pk)
    posts = Post.objects.filter(category=category)
    return render(request, "studentforum/category_posts.html", {"category": category, "posts": posts})


@login_required
def create_category(request):
    if not request.user.is_staff:
        messages.error(request, "Only admins can create categories.")
        return redirect("category_list")
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category created!")
            return redirect("category_list")
    else:
        form = CategoryForm()
    return render(request, "studentforum/create_category.html", {"form": form})


@login_required
def edit_category(request, pk):
    if not request.user.is_staff:
        messages.error(request, "Only admins can edit categories.")
        return redirect("category_list")
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated!")
            return redirect("category_list")
    else:
        form = CategoryForm(instance=category)
    return render(request, "studentforum/create_category.html", {"form": form, "category": category})
