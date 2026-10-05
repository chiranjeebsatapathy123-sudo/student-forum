import importlib
import os

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Category, Post


class BasicViewsTest(TestCase):

    def test_home_status(self):
        resp = self.client.get(reverse("home"))
        self.assertEqual(resp.status_code, 200)

    def test_register_and_login(self):
        # register
        self.client.post(
            reverse("register"),
            {
                "username": "tester",
                "email": "t@example.com",
                "password1": "strongPassword123",
                "password2": "strongPassword123",
            },
            follow=True,
        )
        # user should exist and session should have an auth id
        from django.contrib.auth import get_user_model

        UserModel = get_user_model()
        self.assertTrue(UserModel.objects.filter(username="tester").exists())
        self.assertIn("_auth_user_id", self.client.session)

    def test_create_post_requires_login(self):
        category = Category.objects.create(name="General")
        url = reverse("create_post")
        resp = self.client.post(url, {"title": "Hello", "description": "World", "category": category.pk})
        # should redirect to login
        self.assertEqual(resp.status_code, 302)
        # login and create
        User.objects.create_user("u1", "u1@example.com", "pass1234")
        self.client.login(username="u1", password="pass1234")
        resp = self.client.post(url, {"title": "Hello", "description": "World", "category": category.pk}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(Post.objects.filter(title="Hello").exists())

class NewFeaturesTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="test1", password="password123")
        self.user2 = User.objects.create_user(username="test2", password="password123")
        self.category = Category.objects.create(name="Tech")
        self.post = Post.objects.create(title="Title", description="Desc", user=self.user1, category=self.category)
        
    def test_user_profile_created_on_registration(self):
        self.client.post(reverse("register"), {
            "username": "newuser", "email": "n@e.com", 
            "password1": "strongPassword123!", "password2": "strongPassword123!"
        })
        new_user = User.objects.get(username="newuser")
        self.assertTrue(hasattr(new_user, 'profile'))
        
    def test_upvote_post(self):
        self.client.login(username="test2", password="password123")
        resp = self.client.post(reverse("upvote_post", args=[self.post.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(self.post.upvotes.count(), 1)
        self.assertEqual(self.post.score, 1)
        
    def test_bookmark_post(self):
        self.client.login(username="test2", password="password123")
        resp = self.client.post(reverse("bookmark_post", args=[self.post.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(self.user2.bookmarks.count(), 1)

    def test_ai_copilot_endpoint(self):
        self.client.login(username="test1", password="password123")
        resp = self.client.post(reverse("ai_copilot"), '{"action": "improve", "content": "hello"}', content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("result", resp.json())

