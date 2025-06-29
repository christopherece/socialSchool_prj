from django.db import models
from django.conf import settings
from django.utils import timezone

NOTIFICATION_TYPES = (
    ('like', 'Like'),
    ('comment', 'Comment'),
    ('follow', 'Follow'),
    ('message', 'Message'),
    ('post', 'Post'),
)

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='system_notifications', on_delete=models.CASCADE)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_system_notifications', on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    target_id = models.IntegerField(null=True, blank=True)
    target_content_type = models.CharField(max_length=100, null=True, blank=True)
    message = models.TextField()
    url = models.URLField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.actor.username} -> {self.user.username}: {self.notification_type}'

    def get_url(self):
        """Generate URL based on notification type"""
        if self.notification_type == 'like':
            return f'/posts/{self.target_id}/'
        elif self.notification_type == 'comment':
            return f'/posts/{self.target_id}/'
        elif self.notification_type == 'follow':
            return f'/users/{self.actor.username}/'
        elif self.notification_type == 'message':
            return f'/messaging/conversation/{self.target_id}/'
        elif self.notification_type == 'post':
            return f'/posts/{self.target_id}/'
        return '/system-notifications/'

    def mark_as_read(self):
        self.is_read = True
        self.save()

    def mark_as_unread(self):
        self.is_read = False
        self.save()

    @staticmethod
    def get_unread_count(user):
        return Notification.objects.filter(user=user, is_read=False).count()
