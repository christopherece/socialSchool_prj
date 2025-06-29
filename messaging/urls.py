from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('conversation/<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    path('start/<str:username>/', views.start_conversation, name='start_conversation'),
    path('api/conversation/<int:conversation_id>/send/', views.send_message_ajax, name='send_message_ajax'),
    path('api/conversation/<int:conversation_id>/messages/<int:last_message_id>/', views.get_new_messages, name='get_new_messages'),
    path('api/conversation/<int:conversation_id>/typing/', views.typing_status, name='typing_status'),
    path('api/unread-count/', views.unread_message_count, name='unread_message_count'),
]
