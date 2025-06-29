from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Notification, Message
from django.views.decorators.http import require_POST
from django.utils import timezone

@login_required
def notification_list(request):
    notifications = request.user.received_notifications.all()
    return render(request, 'user_notifications/notification_list.html', {
        'notifications': notifications
    })

@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'status': 'success'})

@login_required
def message_list(request):
    messages = request.user.received_messages.all()
    return render(request, 'user_notifications/message_list.html', {
        'messages': messages
    })

@login_required
def mark_message_read(request, message_id):
    message = get_object_or_404(Message, id=message_id, recipient=request.user)
    message.is_read = True
    message.save()
    return JsonResponse({'status': 'success'})

@login_required
def send_message(request):
    if request.method == 'POST':
        recipient_id = request.POST.get('recipient_id')
        content = request.POST.get('content')
        
        if recipient_id and content:
            recipient = get_object_or_404(User, id=recipient_id)
            Message.objects.create(
                sender=request.user,
                recipient=recipient,
                content=content
            )
            return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})
