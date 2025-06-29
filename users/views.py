from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from .forms import UserRegistrationForm, ProfileForm

User = get_user_model()

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully!')
            return redirect('users:login')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = user.post_set.all()[:5]  # Show 5 recent posts
    
    # Get recent activity
    recent_activity = []
    
    # Add posts to activity
    for post in posts:
        recent_activity.append({
            'icon': 'comment',
            'description': f'Created post "{post.text[:50]}..."',
            'timestamp': post.created_at
        })
    
    # Add comments to activity
    comments = user.comment_set.all()[:5]
    for comment in comments:
        recent_activity.append({
            'icon': 'comments',
            'description': f'Commented on "{comment.post.text[:50]}..."',
            'timestamp': comment.created_at
        })
    
    # Sort activity by timestamp
    recent_activity.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return render(request, 'users/profile.html', {
        'profile_user': user,
        'posts': posts,
        'recent_activity': recent_activity
    })

@login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('users:profile', username=user.username)
    else:
        form = ProfileForm(instance=user)
    return render(request, 'users/edit_profile.html', {'form': form})
