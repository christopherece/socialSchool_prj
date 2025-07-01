from django.db import models
from django.conf import settings
from django.utils import timezone
from notifications.utils import create_notification

MEDIA_TYPES = [
    ('none', 'None'),
    ('image', 'Images'),
    ('video', 'Video'),
    ('file', 'Files'),
    ('mixed', 'Mixed')
]

class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField(max_length=1000, blank=True)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES, default='none', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Post by {self.user.username} on {self.created_at}"

    def get_absolute_url(self):
        return reverse('posts:detail', args=[self.id])

class PostImage(models.Model):
    post = models.ForeignKey(Post, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='post_images/%Y/%m/%d/', max_length=255, blank=True, null=True)
    
    def __str__(self):
        return f"Image for post {self.post.id}"

    def save(self, *args, **kwargs):
        # Ensure the image is saved with the correct path
        super().save(*args, **kwargs)

class PostVideo(models.Model):
    post = models.OneToOneField(Post, related_name='video', on_delete=models.CASCADE)
    video = models.FileField(upload_to='post_videos/%Y/%m/%d/', max_length=255, blank=True, null=True)
    
    def __str__(self):
        return f"Video for post {self.post.id}"

    def save(self, *args, **kwargs):
        # Ensure the video is saved with the correct path
        super().save(*args, **kwargs)

class PostFile(models.Model):
    post = models.ForeignKey(Post, related_name='files', on_delete=models.CASCADE)
    file = models.FileField(upload_to='post_files/%Y/%m/%d/', max_length=255, blank=True, null=True)
    file_type = models.CharField(max_length=10, choices=[
        ('pdf', 'PDF'),
        ('docx', 'DOCX'),
        ('pptx', 'PPTX'),
        ('zip', 'ZIP')
    ])
    
    def __str__(self):
        return f"File for post {self.post.id}"

    def save(self, *args, **kwargs):
        # Ensure the file is saved with the correct path
        super().save(*args, **kwargs)

class Like(models.Model):
    post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('post', 'user')
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Like by {self.user.username} on post {self.post.id}"

    @classmethod
    def get_likes_count(cls, post):
        try:
            return cls.objects.filter(post=post).count()
        except Exception as e:
            print(f"Error in get_likes_count: {str(e)}")
            return 0

    @classmethod
    def toggle_like(cls, post, user):
        """Toggle like status for a post by a user"""
        try:
            # Use get_or_create to handle both cases
            like, created = cls.objects.get_or_create(post=post, user=user)
            
            if created:
                # If new like was created, return True (liked)
                return True, True
            else:
                # If like existed, delete it and return False (unliked)
                like.delete()
                return False, True
                
        except Exception as e:
            print(f"Error in toggle_like: {str(e)}")
            return None, False  # (liked_status, success)


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Comment by {self.user.username} on post {self.post.id}"
    
    def is_reply(self):
        return self.parent is not None

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Create notification if this is a comment (not a reply) and not self-comment
        if not self.parent and self.post.user != self.user:
            create_notification(
                user=self.post.user,
                actor=self.user,
                notification_type='comment',
                message=f'{self.user.username} commented on your post',
                post=self.post,
                url=self.post.get_absolute_url()
            )
