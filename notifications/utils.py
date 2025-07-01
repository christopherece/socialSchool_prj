from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth import get_user_model

# Avoid circular import by using get_user_model
User = get_user_model()

def create_notification(user, actor, notification_type, message, post=None, url=None):
    """Create a notification for a user"""
    try:
        notification = Notification.objects.create(
            sender=actor,
            recipient=user,
            notification_type=notification_type,
            content=message,
            post=post,
            url=url
        )
        return notification
    except Exception as e:
        print(f"Error creating notification: {str(e)}")
        return None
