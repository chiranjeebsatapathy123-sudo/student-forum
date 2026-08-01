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
