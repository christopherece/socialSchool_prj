from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('<str:user_id>/', views.notifications, name='notifications'),
    path('mark-as-read/<str:user_id>/<int:notification_id>/', views.mark_as_read, name='mark_as_read'),
    path('mark-all-as-read/<str:user_id>/', views.mark_all_as_read, name='mark_all_as_read'),
    path('clear-all/<str:user_id>/', views.clear_all_notifications, name='clear_all'),
    path('get-unread-count/<str:user_id>/', views.get_unread_count, name='get_unread_count'),
]
