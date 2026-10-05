from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Post, Comment, Category, Bookmark
from .forms import UserRegisterForm, PostForm, CommentForm, CategoryForm, UserUpdateForm
from .utils import apply_bootstrap_classes
from .rate_limit import rate_limit


def home(request):
    query = request.GET.get("q", "")
    category_id = request.GET.get("category", "")
    tag = request.GET.get("tag", "")
    author = request.GET.get("author", "")
    filter_by = request.GET.get("filter", "")
    from django.db.models import Count
    posts = Post.objects.select_related('user', 'category').annotate(
        comment_count=Count('comments', distinct=True),
        upvote_count=Count('upvotes', distinct=True)
    )

    if query:
        posts = posts.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(tags__icontains=query))
    if category_id:
        posts = posts.filter(category_id=category_id)
    if tag:
        posts = posts.filter(tags__icontains=tag)
    if author:
        posts = posts.filter(user__username__icontains=author)
        
    if filter_by == "unanswered":
        posts = posts.filter(comment_count=0).order_by("-created_date")
    elif filter_by == "solved":
        posts = posts.filter(is_solved=True).order_by("-created_date")
    elif filter_by == "popular":
        # Trending Engine (Phase 4): Votes + Views + Comments
        posts = posts.order_by("-upvote_count", "-views", "-comment_count", "-created_date")
    elif filter_by == "following" and request.user.is_authenticated:
        # Personalized Home Feed (Phase 3)
        following_users = request.user.profile.following_users.values_list('user_id', flat=True)
        following_communities = request.user.followed_communities.all()
        posts = posts.filter(Q(user_id__in=following_users)).order_by("-created_date")
    elif filter_by == "for_you" and request.user.is_authenticated:
        # Recommendation Engine (Phase 5) - Mock logic mixing popular & new
        posts = posts.order_by("-upvote_count", "?", "-created_date")
    else:
        posts = posts.order_by("-created_date")

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


@rate_limit('register', 5, 3600) # 5 per hour
def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            from .models import UserProfile
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, f"Welcome, {user.username}! Your account has been created.")
            return redirect("dashboard")
    else:
        form = UserRegisterForm()
    return render(request, "studentforum/register.html", {"form": form})


@rate_limit('login', 10, 300) # 10 per 5 mins
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
    from django.db.models import Count
    user_posts = Post.objects.filter(user=request.user).select_related('category').annotate(comment_count=Count('comments')).order_by("-created_date")
    user_comments = Comment.objects.filter(user=request.user).select_related('post').order_by("-created_date")
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
    from .forms import UserProfileForm
    from .models import UserProfile
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = UserUpdateForm(request.POST, instance=request.user)
        p_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid() and p_form.is_valid():
            form.save()
            p_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("dashboard")
    else:
        form = UserUpdateForm(instance=request.user)
        p_form = UserProfileForm(instance=profile)
    return render(request, "studentforum/edit_profile.html", {"form": form, "p_form": p_form})


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
@rate_limit('post', 20, 3600) # 20 posts per hour
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
    post = get_object_or_404(Post.objects.select_related('user', 'category'), pk=pk)
    comments = post.comments.select_related('user').all()
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

    related_posts = Post.objects.filter(
        Q(category=post.category) | Q(tags__icontains=post.tags.split(',')[0] if post.tags else '')
    ).exclude(pk=post.pk).distinct()[:3]

    poll = None
    try:
        if hasattr(post, 'poll'):
            poll = post.poll
    except Exception:
        pass

    return render(
        request,
        "studentforum/post_detail.html",
        {
            "post": post,
            "comments": comments,
            "comment_form": comment_form,
            "related_posts": related_posts,
            "poll": poll,
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
    from django.db.models import Count
    category = get_object_or_404(Category, pk=pk)
    posts = Post.objects.filter(category=category).select_related('user', 'category').annotate(comment_count=Count('comments'))
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

from django.http import JsonResponse
import json

@login_required
def toggle_upvote_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user in post.upvotes.all():
        post.upvotes.remove(request.user)
    else:
        post.upvotes.add(request.user)
        post.downvotes.remove(request.user)
    return JsonResponse({'score': post.score})

@login_required
def toggle_downvote_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user in post.downvotes.all():
        post.downvotes.remove(request.user)
    else:
        post.downvotes.add(request.user)
        post.upvotes.remove(request.user)
    return JsonResponse({'score': post.score})

@login_required
def toggle_bookmark(request, pk):
    post = get_object_or_404(Post, pk=pk)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, post=post)
    if not created:
        bookmark.delete()
        return JsonResponse({'bookmarked': False})
    return JsonResponse({'bookmarked': True})

@login_required
def toggle_accept_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if comment.post.user != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    if comment.is_accepted:
        comment.is_accepted = False
        comment.post.is_solved = False
    else:
        # Unaccept others
        Comment.objects.filter(post=comment.post).update(is_accepted=False)
        comment.is_accepted = True
        comment.post.is_solved = True
        
    comment.save()
    comment.post.save()
    return JsonResponse({'accepted': comment.is_accepted})

@login_required
@rate_limit('ai', 10, 60) # 10 AI requests per minute
def ai_copilot(request):
    if request.method == "POST":
        data = json.loads(request.body)
        action = data.get('action')
        content = data.get('content', '')
        
        # Simple dummy responses for the AI
        response_text = ""
        if action == "improve":
            response_text = "Here is an improved version: " + content + "\n\nConsider adding more details and context."
        elif action == "explain":
            response_text = "**AI Explanation:**\nThis concept revolves around breaking down a complex problem into smaller, manageable parts. Think of it as organizing a large library by first separating books by genre, then by author. It increases efficiency and readability."
        elif action == "summarize":
            response_text = "**AI Summary:**\n- **Problem:** The original author is struggling with data structures.\n- **Solution:** Community suggested using HashMaps for O(1) lookups.\n- **Takeaway:** Always consider time-complexity when dealing with large datasets."
        elif action == "analyze_quality":
            return JsonResponse({'score': 85, 'checks': ['Clear question', 'Context provided']})
        elif action == "mcq":
            response_text = "**Practice MCQ:**\nWhat is the primary advantage of a HashMap?\n\nA) Sorted data\nB) O(1) average time complexity for lookups\nC) Uses less memory than an array\nD) Allows duplicate keys\n\n*(Correct Answer: B)*"
        elif action == "flashcards":
            response_text = "**Flashcards Generated:**\n\n**Front:** What is Polymorphism?\n**Back:** The ability of different classes to respond to the same method call in their own way.\n\n**Front:** What is Encapsulation?\n**Back:** Bundling data and methods into a single unit (class) and restricting access to some of the object's components."
        elif action == "notes":
            response_text = "**Revision Notes:**\n\n# Data Structures Review\n1. **Arrays**: Fixed size, O(1) access.\n2. **Linked Lists**: Dynamic size, O(n) access, O(1) insertion/deletion at known points.\n3. **Trees**: Hierarchical data, O(log n) access for balanced BSTs."
        elif action == "path":
            response_text = "**Learning Path Generated:**\n\nStep 1: Introduction to syntax.\nStep 2: Control flow (if/else, loops).\nStep 3: Functions and Scope.\nStep 4: Object-Oriented Programming.\nStep 5: File I/O and Error Handling."
        else:
            response_text = "I am your AI study assistant. How can I help you learn?"
            
        return JsonResponse({'result': response_text})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def check_duplicates(request):
    if request.method == "POST":
        data = json.loads(request.body)
        title = data.get('title', '')
        
        if len(title) < 5:
            return JsonResponse({'duplicates': []})
            
        similars = Post.objects.filter(title__icontains=title).exclude(is_draft=True)[:3]
        
        results = []
        for p in similars:
            score = max(40, 100 - abs(len(p.title) - len(title)) * 2)
            results.append({
                'id': p.pk,
                'title': p.title,
                'score': score,
                'url': f"/post/{p.pk}/"
            })
            
        return JsonResponse({'duplicates': results})
    return JsonResponse({'error': 'Invalid request'}, status=400)


def community_list(request):
    from .models import Community
    from django.db.models import Count
    communities = Community.objects.annotate(member_count=Count('followers')).order_by('-member_count')
    return render(request, "studentforum/community_list.html", {"communities": communities})


def community_detail(request, pk):
    from .models import Community
    community = get_object_or_404(Community, pk=pk)
    
    # Simple trending engine logic (recent + highly engaged)
    # Django 1.11+ can order by calculated annotations, or we just order by upvotes/views for now
    from django.db.models import Count
    events = community.events.all()[:5]
    return render(request, "studentforum/community_detail.html", {
        "community": community,
        "events": events
    })

@login_required
def toggle_follow_community(request, pk):
    from .models import Community
    community = get_object_or_404(Community, pk=pk)
    if request.user in community.followers.all():
        community.followers.remove(request.user)
        following = False
    else:
        community.followers.add(request.user)
        following = True
    return JsonResponse({'following': following, 'count': community.followers.count()})

@login_required
def toggle_follow_user(request, username):
    from django.contrib.auth.models import User
    target_user = get_object_or_404(User, username=username)
    profile = request.user.profile
    if target_user.profile in profile.following_users.all():
        profile.following_users.remove(target_user.profile)
        following = False
    else:
        profile.following_users.add(target_user.profile)
        following = True
    return JsonResponse({'following': following})

@login_required
def vote_poll(request, pk):
    if request.method == "POST":
        from .models import Poll, PollChoice, PollVote
        data = json.loads(request.body)
        choice_id = data.get('choice_id')
        poll = get_object_or_404(Poll, pk=pk)
        
        if PollVote.objects.filter(poll=poll, user=request.user).exists():
            return JsonResponse({'error': 'You have already voted.'}, status=400)
            
        choice = get_object_or_404(PollChoice, pk=choice_id, poll=poll)
        PollVote.objects.create(poll=poll, choice=choice, user=request.user)
        
        # Return updated counts
        total_votes = poll.votes.count()
        choices = []
        for c in poll.choices.all():
            c_votes = c.votes.count()
            choices.append({
                'id': c.id,
                'votes': c_votes,
                'percentage': int((c_votes / total_votes) * 100) if total_votes > 0 else 0
            })
            
        return JsonResponse({'success': True, 'total': total_votes, 'choices': choices})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def practice_mode(request):
    return render(request, "studentforum/practice.html")

@login_required
def moderation_dashboard(request):
    if not request.user.is_staff:
        return redirect("home")
    # For now, just rendering a basic template
    return render(request, "studentforum/moderation.html")

@login_required
def project_list(request):
    from .models import Project
    projects = Project.objects.all()
    return render(request, "studentforum/projects.html", {"projects": projects})

@login_required
def careers_portal(request):
    from .models import JobPosting, InterviewExperience
    jobs = JobPosting.objects.filter(is_active=True).order_by('-created_date')
    experiences = InterviewExperience.objects.all().order_by('-created_date')
    return render(request, "studentforum/careers.html", {"jobs": jobs, "experiences": experiences})

@login_required
def leaderboard(request):
    from .models import UserProfile
    top_users = UserProfile.objects.all().order_by('-reputation')[:20]
    return render(request, "studentforum/leaderboard.html", {"top_users": top_users})

@login_required
def chat_room(request, room_name):
    return render(request, "studentforum/chat.html", {"room_name": room_name})

@login_required
def university_dashboard(request):
    if not request.user.profile.is_university_admin:
        messages.error(request, "You are not authorized to view the University Admin Portal.")
        return redirect("dashboard")
        
    from .models import UserProfile
    uni_students = UserProfile.objects.filter(university_name=request.user.profile.university_name)
    total_students = uni_students.count()
    return render(request, "studentforum/university_dashboard.html", {
        "uni_students": uni_students,
        "total_students": total_students,
        "university_name": request.user.profile.university_name
    })
