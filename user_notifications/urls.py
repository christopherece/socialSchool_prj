from django.urls import path
from . import views

app_name = 'user_notifications'

urlpatterns = [
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('messages/', views.message_list, name='message_list'),
    path('messages/<int:message_id>/read/', views.mark_message_read, name='mark_message_read'),
    path('messages/send/', views.send_message, name='send_message'),
]
