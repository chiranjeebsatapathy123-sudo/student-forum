from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.contrib.auth.models import User
from forum.models import Post
from django.utils import timezone
import datetime

class Command(BaseCommand):
    help = 'Sends a weekly digest email of top posts to all active users.'

    def handle(self, *args, **kwargs):
        last_week = timezone.now() - datetime.timedelta(days=7)
        top_posts = Post.objects.filter(created_date__gte=last_week).order_by('-views')[:3]
        
        if not top_posts:
            self.stdout.write("No top posts this week to send.")
            return

        subject = "Your Student Knowledge Hub Weekly Digest \U0001F680"
        
        message_body = "Here are the top trending discussions this week:\n\n"
        for post in top_posts:
            message_body += f"- {post.title} (Views: {post.views})\n  Link: http://127.0.0.1:8000/post/{post.id}/\n\n"
        
        message_body += "Keep learning and sharing!\n- The Student Forum Team"

        users = User.objects.filter(is_active=True).values_list('email', flat=True)
        recipient_list = [email for email in users if email]

        if recipient_list:
            send_mail(
                subject,
                message_body,
                'no-reply@studenthub.com',
                recipient_list,
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS(f"Successfully sent weekly digest to {len(recipient_list)} users."))
        else:
            self.stdout.write(self.style.WARNING("No active users with valid emails found."))
