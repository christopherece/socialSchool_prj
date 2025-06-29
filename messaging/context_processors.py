from django.conf import settings
from django.contrib.auth import get_user_model
from .models import Message

def unread_message_count(request):
    if request.user.is_authenticated:
        conversations = request.user.conversation_set.all()
        unread_count = Message.objects.filter(
            conversation__in=conversations,
            is_read=False,
            sender__in=conversations.values('participants').exclude(participants=request.user)
        ).count()
        return {'unread_message_count': unread_count}
    return {'unread_message_count': 0}
