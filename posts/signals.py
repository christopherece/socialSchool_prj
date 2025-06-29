from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Comment
from notifications.utils import create_notification

@receiver(post_save, sender=Comment)
def create_comment_notification(sender, instance, created, **kwargs):
    """Create notification when a user comments on someone else's post"""
    if created and instance.post.user != instance.user:
        create_notification(
            user=instance.post.user,
            actor=instance.user,
            notification_type='comment',
            message=f'{instance.user.username} commented on your post',
            target_id=instance.post.id,
            target_content_type='post'
        )
