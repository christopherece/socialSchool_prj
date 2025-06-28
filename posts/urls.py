from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.home, name='home'),
    path('create/', views.create_post, name='create'),
    path('post/<int:pk>/', views.post_detail, name='detail'),
    path('post/<int:pk>/edit/', views.edit_post, name='edit'),
    path('post/<int:pk>/delete/', views.delete_post, name='delete'),
    path('post/<int:pk>/like/', views.like_post, name='like'),
    path('post/<int:pk>/comment/', views.add_comment, name='comment'),
]
