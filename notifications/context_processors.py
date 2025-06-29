from django.conf import settings
from .models import Notification

def notification_count(request):
    if request.user.is_authenticated:
        unread_count = request.user.system_notifications.filter(
            is_read=False
        ).count()
        
        recent_notifications = request.user.system_notifications.order_by('-created_at')[:5]
        
        return {
            'unread_notifications': unread_count,
            'recent_notifications': recent_notifications
        }
    return {
        'unread_notifications': 0,
        'recent_notifications': []
    }
