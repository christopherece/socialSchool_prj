from .models import Notification
from django.contrib.auth import get_user_model
from django.urls import reverse

def create_notification(user, actor, notification_type, message, target_id=None, target_content_type=None, target_url=None):
    """Create a notification for a user"""
    notification = Notification(
        user=user,
        actor=actor,
        notification_type=notification_type,
        message=message
    )
    
    if target_id and target_content_type:
        notification.target_id = target_id
        notification.target_content_type = target_content_type
        
        # Set the notification URL based on content type
        if target_content_type == 'post':
            if target_url:
                notification.url = target_url
            else:
                notification.url = reverse('posts:detail', args=[target_id])
        # Add more content types as needed
        
    notification.save()
    return notification
