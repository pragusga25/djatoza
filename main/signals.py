from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from .models import LoginLog


@receiver(user_logged_in)
def log_user_login(sender, user, request, **kwargs):
    """Log user login activity"""
    LoginLog.objects.create(user=user, action="login")


@receiver(user_logged_out)
def log_user_logout(sender, user, request, **kwargs):
    """Log user logout activity"""
    if user:  # Anonymous user check
        LoginLog.objects.create(user=user, action="logout")
