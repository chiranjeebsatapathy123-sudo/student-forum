from django.contrib import admin
from .models import Category, Post, Comment, UserProfile, Bookmark, Notification
from django.db.models import Count

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "department", "reputation"]
    search_fields = ["user__username", "department"]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "post_count", "created_date"]
    search_fields = ["name"]
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(_post_count=Count('posts'))
        
    def post_count(self, obj):
        return obj._post_count
    post_count.admin_order_field = '_post_count'

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["title", "user", "category", "created_date", "is_solved"]
    list_filter = ["category", "created_date", "is_solved"]
    search_fields = ["title", "description", "user__username"]
    date_hierarchy = "created_date"

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["user", "post", "created_date", "is_accepted"]
    list_filter = ["created_date", "is_accepted"]
    search_fields = ["comment_text", "user__username", "post__title"]

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ["user", "post", "created_at"]
    
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["user", "message", "is_read", "created_at"]
