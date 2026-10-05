from django.urls import path, include
from rest_framework import routers
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from forum import views, api

# DRF Router setup
router = routers.DefaultRouter()
router.register(r'posts', api.PostViewSet)
router.register(r'categories', api.CategoryViewSet)

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("password/change/", views.change_password, name="change_password"),
    path("post/create/", views.create_post, name="create_post"),
    path("post/<int:pk>/", views.post_detail, name="post_detail"),
    path("post/<int:pk>/edit/", views.edit_post, name="edit_post"),
    path("post/<int:pk>/delete/", views.delete_post, name="delete_post"),
    path("comment/<int:pk>/edit/", views.edit_comment, name="edit_comment"),
    path("comment/<int:pk>/delete/", views.delete_comment, name="delete_comment"),
    path("categories/", views.category_list, name="category_list"),
    path("category/<int:pk>/", views.category_posts, name="category_posts"),
    path("category/create/", views.create_category, name="create_category"),
    path("category/<int:pk>/edit/", views.edit_category, name="edit_category"),
    
    # New interaction endpoints
    path("post/<int:pk>/upvote/", views.toggle_upvote_post, name="upvote_post"),
    path("post/<int:pk>/downvote/", views.toggle_downvote_post, name="downvote_post"),
    path("post/<int:pk>/bookmark/", views.toggle_bookmark, name="bookmark_post"),
    path("comment/<int:pk>/accept/", views.toggle_accept_comment, name="accept_comment"),
    path("api/ai_copilot/", views.ai_copilot, name="ai_copilot"),
    path("api/check_duplicates/", views.check_duplicates, name="check_duplicates"),
    path("communities/", views.community_list, name="community_list"),
    path("community/<int:pk>/", views.community_detail, name="community_detail"),
    path("community/<int:pk>/follow/", views.toggle_follow_community, name="toggle_follow_community"),
    path("user/<str:username>/follow/", views.toggle_follow_user, name="toggle_follow_user"),
    path("poll/<int:pk>/vote/", views.vote_poll, name="vote_poll"),
    path("practice/", views.practice_mode, name="practice"),
    path("moderation/", views.moderation_dashboard, name="moderation_dashboard"),
    path("projects/", views.project_list, name="project_list"),
    path("careers/", views.careers_portal, name="careers_portal"),
    path("leaderboard/", views.leaderboard, name="leaderboard"),
    path("chat/<str:room_name>/", views.chat_room, name="chat_room"),
    path("university/", views.university_dashboard, name="university_dashboard"),
    path("courses/", views.course_list, name="course_list"),
    path("analytics/", views.analytics_dashboard, name="analytics_dashboard"),
    
    # REST API endpoints
    path("api/v1/", include(router.urls)),
    
    # OpenAPI Docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
