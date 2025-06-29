from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from .models import Conversation, Message
from django.utils import timezone
from django.contrib.auth import get_user_model
User = get_user_model()

@login_required
def inbox(request):
    conversations = Conversation.objects.filter(participants=request.user).order_by('-updated_at')
    conversations_with_other_users = []
    for conversation in conversations:
        other_user = conversation.participants.exclude(id=request.user.id).first()
        conversations_with_other_users.append({
            'conversation': conversation,
            'other_user': other_user
        })
    # Get active users (excluding the current user)
    active_users = User.objects.exclude(id=request.user.id).order_by('username')
    
    # Get messages for the most recent conversation if any
    if conversations:
        recent_conversation = conversations.first()
        messages = Message.objects.filter(conversation=recent_conversation).order_by('created_at')
        other_user = conversations_with_other_users[0]['other_user']
    else:
        messages = []
        recent_conversation = None
        other_user = None
    
    return render(request, 'messaging/inbox.html', {
        'conversations': conversations_with_other_users,
        'conversation': recent_conversation,
        'messages': messages,
        'other_user': other_user,
        'active_users': active_users
    })

@login_required
def conversation_detail(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    if not conversation.participants.filter(id=request.user.id).exists():
        return redirect('messaging:inbox')
    
    messages = Message.objects.filter(conversation=conversation).order_by('created_at')
    unread_messages = messages.filter(is_read=False).exclude(sender=request.user)
    unread_messages.update(is_read=True)
    
    other_user = conversation.participants.exclude(id=request.user.id).first()
    return render(request, 'messaging/conversation.html', {
        'conversation': conversation,
        'messages': messages,
        'other_user': other_user
    })

@login_required
def start_conversation(request, username):
    other_user = get_object_or_404(User, username=username)
    if other_user == request.user:
        return redirect('messaging:inbox')
    
    conversation = Conversation.objects.filter(
        participants=request.user
    ).filter(
        participants=other_user
    ).first()
    
    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, other_user)
    
    return redirect('messaging:conversation_detail', conversation_id=conversation.id)

@login_required
def send_message_ajax(request, conversation_id):
    if request.method == 'POST':
        conversation = get_object_or_404(Conversation, id=conversation_id)
        content = request.POST.get('content', '').strip()
        
        if content:
            message = Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content
            )
            
            # Create notification for the other participant
            other_user = conversation.participants.exclude(id=request.user.id).first()
            if other_user:
                from notifications.utils import create_notification
                create_notification(
                    user=other_user,
                    actor=request.user,
                    notification_type='message',
                    message=f'{request.user.username} sent you a message',
                    target_id=conversation.id,
                    target_content_type='conversation'
                )
            
            return JsonResponse({
                'status': 'success',
                'message_id': message.id,
                'message_content': message.content,
                'timestamp': message.created_at.strftime('%b %d, %Y, %I:%M %p'),
                'sender_id': request.user.id,
                'is_read': False
            })
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def get_new_messages(request, conversation_id, last_message_id):
    try:
        conversation = Conversation.objects.get(id=conversation_id)
        if request.user not in conversation.participants.all():
            return JsonResponse({'error': 'Unauthorized'}, status=403)
            
        # Get new messages since last_message_id
        messages = Message.objects.filter(
            conversation=conversation,
            id__gt=last_message_id
        ).order_by('created_at')
        
        # Mark messages as read for this user
        unread_messages = messages.filter(is_read=False)
        if unread_messages.exists():
            unread_messages.update(is_read=True)
            
        message_data = []
        for message in messages:
            message_data.append({
                'id': message.id,
                'content': message.content,
                'timestamp': message.created_at.strftime('%b %d, %Y %H:%M'),
                'sender': message.sender.username,
                'is_unread': not message.is_read
            })
            
        return JsonResponse({'messages': message_data})
    except Conversation.DoesNotExist:
        return JsonResponse({'error': 'Conversation not found'}, status=404)

@login_required
def unread_message_count(request):
    conversations = request.user.conversation_set.all()
    unread_count = Message.objects.filter(
        conversation__in=conversations,
        is_read=False,
        sender__in=conversations.values('participants').exclude(participants=request.user)
    ).count()
    return JsonResponse({'count': unread_count})

@login_required
def typing_status(request, conversation_id):
    try:
        conversation = Conversation.objects.get(id=conversation_id)
        if request.user not in conversation.participants.all():
            return JsonResponse({'error': 'Unauthorized'}, status=403)
            
        # This endpoint will be used to check if the other user is typing
        # For now, we'll just return a dummy response
        return JsonResponse({'is_typing': False})
    except Conversation.DoesNotExist:
        return JsonResponse({'error': 'Conversation not found'}, status=404)
