from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Notification

@login_required
def notifications(request, user_id):
    if str(request.user.id) != user_id:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
    
    notifications = request.user.system_notifications.all()
    unread_count = Notification.get_unread_count(request.user)
    context = {
        'notifications': notifications,
        'unread_count': unread_count
    }
    return render(request, 'notifications/notifications.html', context)

@login_required
def mark_as_read(request, user_id, notification_id):
    if str(request.user.id) != user_id:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
    
    try:
        notification = get_object_or_404(Notification, id=notification_id, user=request.user)
        notification.mark_as_read()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
def mark_all_as_read(request, user_id):
    if str(request.user.id) != user_id:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
    
    notifications = Notification.objects.filter(user=request.user)
    notifications.update(is_read=True)
    return JsonResponse({'status': 'success'})

@login_required
def get_unread_count(request, user_id):
    if str(request.user.id) != user_id:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
    
    count = Notification.get_unread_count(request.user)
    return JsonResponse({'count': count})

@login_required
def clear_all_notifications(request, user_id):
    """Clear all notifications for the current user"""
    if str(request.user.id) != user_id:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
    
    Notification.objects.filter(user=request.user).delete()
    return JsonResponse({'status': 'success'})
