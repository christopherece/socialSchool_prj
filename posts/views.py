from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Count
from .models import Post, PostImage, PostVideo, PostFile, Comment, Like
from .forms import PostForm, CommentForm

from django.core.paginator import Paginator

def home(request):
    posts = Post.objects.all().order_by('-created_at')
    paginator = Paginator(posts, 5)  # Show 5 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Return JSON response for AJAX requests
        posts_html = render_to_string('posts/_post_list.html', {
            'page_obj': page_obj,
            'comment_form': CommentForm(),
            'csrf_token': request.COOKIES.get('csrftoken')
        })
        return JsonResponse({'posts': posts_html, 'has_next': page_obj.has_next()})
    
    return render(request, 'posts/home.html', {
        'page_obj': page_obj,
        'comment_form': CommentForm(),
        'csrf_token': request.COOKIES.get('csrftoken')
    })

@login_required
def create_post(request):
    if request.method == 'POST':
        print("Request POST data:", request.POST)
        print("Request FILES data:", request.FILES)
        
        # Create the form with POST and FILES data
        form = PostForm(request.POST, request.FILES)
        if not form.is_valid():
            print("Form errors:", form.errors)
            # Check if we have FILES data
            if request.FILES:
                print("FILES data exists but form is invalid")
                # Try to save the post first to get the ID
                post = Post(text=request.POST.get('text'), user=request.user)
                post.save()
                
                # Handle images
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
                
                # Handle video
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
                
                # Handle files
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
            # Save the post first
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            print("Post saved successfully")
            
            media_type = form.cleaned_data.get('media_type')
            print("Media type selected:", media_type)
            
            # Handle multiple images
            if media_type in ['image', 'mixed']:
                images = request.FILES.getlist('images')
                print("Images uploaded:", len(images))
                if images:
                    for image in images[:5]:  # Limit to 5 images
                        print("Saving image:", image.name)
                        try:
                            # Create a new PostImage instance
                            post_image = PostImage(post=post, image=image)
                            # Save the image first to ensure it gets a filename
                            post_image.save()
                            print("Image saved successfully")
                        except Exception as e:
                            print(f"Error saving image {image.name}: {str(e)}")
                            messages.error(request, f'Error saving image {image.name}')
                            return redirect('posts:create')
                elif media_type == 'image':  # If media_type is image but no images uploaded
                    messages.error(request, 'Please upload at least one image.')
                    return redirect('posts:create')
            
            # Handle video
            if media_type in ['video', 'mixed']:
                video = request.FILES.get('video')
                print("Video uploaded:", bool(video))
                if video:
                    print("Saving video:", video.name)
                    try:
                        # Create a new PostVideo instance
                        post_video = PostVideo(post=post, video=video)
                        # Save the video
                        post_video.save()
                        print("Video saved successfully")
                    except Exception as e:
                        print(f"Error saving video {video.name}: {str(e)}")
                        messages.error(request, f'Error saving video {video.name}')
                        return redirect('posts:create')
                elif media_type == 'video':  # If media_type is video but no video uploaded
                    messages.error(request, 'Please upload a video.')
                    return redirect('posts:create')
            
            # Handle files
            if media_type in ['file', 'mixed']:
                files = request.FILES.getlist('files')
                print("Files uploaded:", len(files))
                if files:
                    for file in files[:5]:  # Limit to 5 files
                        print("Saving file:", file.name)
                        try:
                            # Create a new PostFile instance
                            post_file = PostFile(post=post, file=file)
                            # Save the file
                            post_file.save()
                            print("File saved successfully")
                        except Exception as e:
                            print(f"Error saving file {file.name}: {str(e)}")
                            messages.error(request, f'Error saving file {file.name}')
                            return redirect('posts:create')
                elif media_type == 'file':  # If media_type is file but no files uploaded
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
            
            # Handle multiple images
            for image in request.FILES.getlist('images'):
                PostImage.objects.create(post=post, image=image)
            
            # Handle video
            if 'video' in request.FILES:
                PostVideo.objects.create(post=post, video=request.FILES['video'])
            
            # Handle files
            for file in request.FILES.getlist('files'):
                PostFile.objects.create(post=post, file=file)
            
            messages.success(request, 'Post updated successfully!')
            return redirect('posts:detail', pk=pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'posts/edit_post.html', {'form': form, 'post': post})

@login_required
def add_comment(request, pk):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        post = get_object_or_404(Post, pk=pk)
        form = CommentForm(request.POST)
        
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            
            return JsonResponse({
                'success': True,
                'comment_id': comment.id,
                'user': {
                    'username': request.user.username,
                    'profile_picture': request.user.profile_picture.url if request.user.profile_picture else None
                },
                'content': comment.content,
                'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M')
            })
        
        return JsonResponse({'error': form.errors.as_json()}, status=400)

@login_required
def like_post(request, pk):
    try:
        # Get the post
        post = get_object_or_404(Post, pk=pk)
        
        # Get the actual user object
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({
                'error': 'User not authenticated',
                'success': False
            }, status=401)
        
        # Toggle the like status
        liked = Like.toggle_like(post, user)
        
        # Get likes count
        likes_count = Like.get_likes_count(post)
        
        # Prepare response
        response_data = {
            'success': True,
            'liked': liked,
            'likes_count': likes_count
        }
        
        # Log the operation
        print(f"Like operation for post {pk} by {user.username}")
        print(f"Success: {liked}, Likes count: {likes_count}")
        
        return JsonResponse(response_data)
        
    except Post.DoesNotExist:
        error_msg = f'Post with ID {pk} does not exist'
        print(f"Error in like_post: {error_msg}")
        return JsonResponse({
            'error': error_msg,
            'success': False
        }, status=404)
    except Exception as e:
        error_msg = str(e)
        print(f"Error in like_post: {error_msg}")
        return JsonResponse({
            'error': f"An unexpected error occurred: {error_msg}",
            'success': False
        }, status=500)

@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.user != request.user:
        messages.error(request, 'You can only delete your own posts.')
        return redirect('posts:detail', pk=pk)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted successfully!')
        return redirect('posts:home')
    return render(request, 'posts/delete_post.html', {'post': post})

@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.all()
    
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            messages.success(request, 'Comment added successfully!')
            return redirect('posts:detail', pk=pk)
    else:
        comment_form = CommentForm()
    
    return render(request, 'posts/post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'user': request.user
    })

@login_required
@require_POST
def like_post(request, pk):
    try:
        post = get_object_or_404(Post, pk=pk)
        
        # Get the actual user object
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({
                'error': 'User not authenticated',
                'success': False
            }, status=401)
        
        # Toggle the like status
        liked = Like.toggle_like(post, user)
        
        # Get likes count
        likes_count = Like.get_likes_count(post)
        
        # Prepare response
        response_data = {
            'success': True,
            'liked': liked,
            'likes_count': likes_count
        }
        
        # Log the operation
        print(f"Like operation for post {pk} by {user.username}")
        print(f"Success: {liked}, Likes count: {likes_count}")
        
        return JsonResponse(response_data)
        
    except Post.DoesNotExist:
        error_msg = f'Post with ID {pk} does not exist'
        print(f"Error in like_post: {error_msg}")
        return JsonResponse({
            'error': error_msg,
            'success': False
        }, status=404)
    except Exception as e:
        error_msg = str(e)
        print(f"Error in like_post: {error_msg}")
        return JsonResponse({
            'error': f"An unexpected error occurred: {error_msg}",
            'success': False
        }, status=500)

@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            return JsonResponse({
                'success': True,
                'comment_id': comment.id,
                'user': comment.user.username,
                'content': comment.content,
                'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M')
            })
    return JsonResponse({'success': False})
