from .models import Notification
from django.contrib.auth import get_user_model
from django.urls import reverse

def create_notification(user, actor, notification_type, message, post=None, url=None):
    """Create a notification for a user if it doesn't already exist"""
    # Check if notification already exists
    existing_notification = Notification.objects.filter(
        sender=actor,
        recipient=user,
        notification_type=notification_type,
        post=post
    ).first()

    if existing_notification:
        # If notification exists, update the message and mark it as unread
        existing_notification.content = message
        existing_notification.is_read = False
        existing_notification.created_at = timezone.now()
        existing_notification.save()
        return existing_notification

    # Create new notification if it doesn't exist
    notification = Notification(
        sender=actor,
        recipient=user,
        notification_type=notification_type,
        content=message
    )
    
    if post:
        notification.post = post
        if url:
            notification.url = url
        else:
            notification.url = reverse('posts:detail', args=[post.id])
    
    notification.save()
    return notification
