from django.contrib import admin
from .models import Category, Post, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "post_count", "created_date"]
    search_fields = ["name"]


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["title", "user", "category", "created_date"]
    list_filter = ["category", "created_date"]
    search_fields = ["title", "description", "user__username"]
    date_hierarchy = "created_date"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["user", "post", "created_date"]
    list_filter = ["created_date"]
    search_fields = ["comment_text", "user__username", "post__title"]
    actions = ["delete_selected"]
