from django.shortcuts import render, redirect, get_object_or_404
import json

from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Count
from django.utils import timezone
from .models import Post, PostImage, PostVideo, PostFile, Comment, Like
from .forms import PostForm, CommentForm
from users.models import CustomUser
from notifications.utils import create_notification

from django.core.paginator import Paginator

@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = Comment.objects.filter(post=post).order_by('-created_at')
    
    # Get likes count
    likes_count = Like.get_likes_count(post)
    
    # Check if current user has liked this post
    user_liked = False
    if request.user.is_authenticated:
        user_liked = Like.objects.filter(post=post, user=request.user).exists()
    
    return render(request, 'posts/post_detail.html', {
        'post': post,
        'comments': comments,
        'likes_count': likes_count,
        'user_liked': user_liked,
        'comment_form': CommentForm()
    })

def home(request):
    posts = Post.objects.all().order_by('-created_at')
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    if request.user.is_authenticated:
        unread_notifications = request.user.received_notifications.filter(is_read=False).count()
        unread_messages = request.user.received_messages.filter(is_read=False).count()
    else:
        unread_notifications = 0
        unread_messages = 0
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        posts_html = render_to_string('posts/_post_list.html', {
            'page_obj': page_obj,
            'comment_form': CommentForm(),
            'csrf_token': request.COOKIES.get('csrftoken')
        }, request=request)
        return JsonResponse({'posts_html': posts_html})
    
    active_users = CustomUser.objects.filter(
        user__last_login__gte=timezone.now() - timezone.timedelta(hours=24)
    ).order_by('-user__last_login')[:5]
    
    return render(request, 'posts/home.html', {
        'page_obj': page_obj,
        'comment_form': CommentForm(),
        'csrf_token': request.COOKIES.get('csrftoken'),
        'active_users': active_users
    })

@login_required
def create_post(request):
    if request.method == 'POST':
        print("Request POST data:", request.POST)
        print("Request FILES data:", request.FILES)
        
        form = PostForm(request.POST, request.FILES)
        if not form.is_valid():
            print("Form errors:", form.errors)
            if request.FILES:
                print("FILES data exists but form is invalid")
                post = Post(text=request.POST.get('text'), user=request.user)
                post.save()
                
                if 'images' in request.FILES:
                    images = request.FILES.getlist('images')
                    print("Images found in FILES:", len(images))
                    for image in images[:5]:
                        try:
                            PostImage.objects.create(post=post, image=image)
                            print("Image saved successfully")
                        except Exception as e:
                            print(f"Error saving image {image.name}: {str(e)}")
                            messages.error(request, f'Error saving image {image.name}')
                            return redirect('posts:create')
                
                if 'video' in request.FILES:
                    video = request.FILES.get('video')
                    if video:
                        try:
                            PostVideo.objects.create(post=post, video=video)
                            print("Video saved successfully")
                        except Exception as e:
                            print(f"Error saving video {video.name}: {str(e)}")
                            messages.error(request, f'Error saving video {video.name}')
                            return redirect('posts:create')
                
                if 'files' in request.FILES:
                    files = request.FILES.getlist('files')
                    print("Files found in FILES:", len(files))
                    for file in files[:5]:
                        try:
                            PostFile.objects.create(post=post, file=file)
                            print("File saved successfully")
                        except Exception as e:
                            print(f"Error saving file {file.name}: {str(e)}")
                            messages.error(request, f'Error saving file {file.name}')
                            return redirect('posts:create')
                
                messages.success(request, 'Post created successfully!')
                return redirect('posts:home')
            else:
                messages.error(request, 'No files were uploaded.')
                return render(request, 'posts/create_post.html', {'form': form})
            
        try:
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            print("Post saved successfully")
            
            media_type = form.cleaned_data.get('media_type')
            print("Media type selected:", media_type)
            
            if media_type in ['image', 'mixed']:
                images = request.FILES.getlist('images')
                print("Images uploaded:", len(images))
                if images:
                    for image in images[:5]:
                        print("Saving image:", image.name)
                        try:
                            post_image = PostImage(post=post, image=image)
                            post_image.save()
                            print("Image saved successfully")
                        except Exception as e:
                            print(f"Error saving image {image.name}: {str(e)}")
                            messages.error(request, f'Error saving image {image.name}')
                            return redirect('posts:create')
                elif media_type == 'image':
                    messages.error(request, 'Please upload at least one image.')
                    return redirect('posts:create')
            
            if media_type in ['video', 'mixed']:
                video = request.FILES.get('video')
                print("Video uploaded:", bool(video))
                if video:
                    print("Saving video:", video.name)
                    try:
                        post_video = PostVideo(post=post, video=video)
                        post_video.save()
                        print("Video saved successfully")
                    except Exception as e:
                        print(f"Error saving video {video.name}: {str(e)}")
                        messages.error(request, f'Error saving video {video.name}')
                        return redirect('posts:create')
                elif media_type == 'video':
                    messages.error(request, 'Please upload a video.')
                    return redirect('posts:create')
            
            if media_type in ['file', 'mixed']:
                files = request.FILES.getlist('files')
                print("Files uploaded:", len(files))
                if files:
                    for file in files[:5]:
                        print("Saving file:", file.name)
                        try:
                            post_file = PostFile(post=post, file=file)
                            post_file.save()
                            print("File saved successfully")
                        except Exception as e:
                            print(f"Error saving file {file.name}: {str(e)}")
                            messages.error(request, f'Error saving file {file.name}')
                            return redirect('posts:create')
                elif media_type == 'file':
                    messages.error(request, 'Please upload at least one file.')
                    return redirect('posts:create')
            
            messages.success(request, 'Post created successfully!')
            return redirect('posts:home')
            
        except Exception as e:
            print("Error in create_post view:", str(e))
            messages.error(request, f'Error creating post: {str(e)}')
            return redirect('posts:create')
    else:
        form = PostForm()
        return render(request, 'posts/create_post.html', {'form': form})

@login_required
def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.user != request.user:
        messages.error(request, 'You can only edit your own posts.')
        return redirect('posts:detail', pk=pk)
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save()
            
            for image in request.FILES.getlist('images'):
                PostImage.objects.create(post=post, image=image)
            
            if 'video' in request.FILES:
                PostVideo.objects.create(post=post, video=request.FILES['video'])
            
            for file in request.FILES.getlist('files'):
                PostFile.objects.create(post=post, file=file)
            
            messages.success(request, 'Post updated successfully!')
            return redirect('posts:detail', pk=pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'posts/edit_post.html', {'form': form, 'post': post})

@login_required
def add_comment(request, pk):
    try:
        print(f"Adding comment for post {pk}")
        post = get_object_or_404(Post, pk=pk)
        print(f"Found post: {post}")
        
        if request.method == 'POST':
            # Handle both form and JSON data
            if request.content_type == 'application/json':
                try:
                    data = json.loads(request.body)
                    content = data.get('content', '')
                    print(f"Received JSON data: {data}")
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {str(e)}")
                    return JsonResponse({'error': 'Invalid JSON data'}, status=400)
            else:
                content = request.POST.get('content', '')
                print(f"Received form data: {content}")
            
            if not content:
                print("No content provided")
                return JsonResponse({'error': 'Comment content is required'}, status=400)
            
            # Create the comment
            print(f"Creating comment for user {request.user.username}")
            comment = Comment.objects.create(
                post=post,
                user=request.user,
                content=content
            )
            print(f"Created comment: {comment}")
            
            # Create notification if user commented on someone else's post
            if post.user != request.user:
                print(f"Creating notification for post owner {post.user.username}")
                create_notification(
                    user=post.user,
                    actor=request.user,
                    notification_type='comment',
                    message=f'{request.user.username} commented on your post',
                    target_id=post.id,
                    target_content_type='post'
                )
            
            return JsonResponse({
                'success': True,
                'comment_id': comment.id,
                'user': {
                    'username': request.user.username,
                    'profile_picture': request.user.custom_user.profile_picture.url if request.user.custom_user.profile_picture else None
                },
                'content': comment.content,
                'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M')
            })
            
        return JsonResponse({'error': 'Invalid request method'}, status=405)
        
    except Exception as e:
        print(f"Error in add_comment: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return JsonResponse({
            'error': f'An unexpected error occurred: {str(e)}',
            'success': False
        }, status=500)

@login_required
def add_reply(request, post_pk, comment_pk):
    post = get_object_or_404(Post, pk=post_pk)
    parent_comment = get_object_or_404(Comment, pk=comment_pk)
    
    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.post = post
            reply.user = request.user
            reply.parent = parent_comment
            reply.save()
            
            # Create notification for the comment author (if different from current user)
            if parent_comment.user != request.user:
                from notifications.utils import create_notification
                create_notification(
                    user=parent_comment.user,
                    actor=request.user,
                    notification_type='reply',
                    message=f'{request.user.username} replied to your comment',
                    target_id=post.id,
                    target_content_type='post'
                )

            # Create notification for the post owner if they're not the one being replied to
            if post.user != request.user and post.user != parent_comment.user:
                create_notification(
                    user=post.user,
                    actor=request.user,
                    notification_type='reply',
                    message=f'{request.user.username} replied to a comment on your post',
                    target_id=post.id,
                    target_content_type='post'
                )
            
            return JsonResponse({
                'success': True,
                'reply_id': reply.id,
                'user': {
                    'username': request.user.username,
                    'profile_picture': request.user.profile_picture.url if request.user.profile_picture else None
                },
                'content': reply.content,
                'created_at': reply.created_at.strftime('%Y-%m-%d %H:%M')
            })
        
        return JsonResponse({'error': form.errors.as_json()}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def like_post(request, pk):
    try:
        # Get the post
        post = get_object_or_404(Post, pk=pk)
        user = request.user
        
        # Toggle the like
        liked = Like.toggle_like(post, user)
        
        # Create notification if user liked the post
        if liked and post.user != user:
            try:
                from notifications.utils import create_notification
                create_notification(
                    user=post.user,
                    actor=user,
                    notification_type='like',
                    message=f'{user.username} liked your post',
                    target_id=post.id,
                    target_content_type='post',
                    target_url=request.build_absolute_uri(post.get_absolute_url())
                )
            except Exception as e:
                print(f"Error creating notification: {str(e)}")
                # Don't return an error if notification fails
        
        # Get the likes count
        likes_count = Like.get_likes_count(post)
        
        # Prepare response
        response_data = {
            'success': True,
            'liked': liked,
            'likes_count': likes_count,
            'user': {
                'username': user.username,
                'profile_picture': user.custom_user.profile_picture.url if user.custom_user.profile_picture else None
            }
        }
        
        # Log the operation
        print(f"Like operation for post {pk} by {user.username}")
        print(f"Success: {liked}, Likes count: {likes_count}")
        
        return JsonResponse(response_data)
        
    except Post.DoesNotExist:
        return JsonResponse({
            'error': 'Post not found',
            'success': False
        }, status=404)
    
    except Exception as e:
        print(f"Error in like_post: {str(e)}")
        return JsonResponse({
            'error': 'Failed to toggle like',
            'success': False
        }, status=500)

@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.user != request.user:
        messages.error(request, 'You can only delete your own posts.')
        return redirect('posts:detail', pk=pk)
    
    post.delete()
    messages.success(request, 'Post deleted successfully!')
    return redirect('posts:home')
