from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('list/', views.event_list, name='list'),
    path('create/', views.create_event, name='create'),
    path('detail/<int:pk>/', views.event_detail, name='detail'),
]
