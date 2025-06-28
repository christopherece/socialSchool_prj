from django.contrib import admin
from .models import Post, PostImage, PostVideo, PostFile, Comment

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'text', 'media_type', 'created_at', 'updated_at')
    list_filter = ('media_type', 'created_at')
    search_fields = ('text', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'

@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'image')
    list_filter = ('post__created_at',)
    search_fields = ('post__text',)

@admin.register(PostVideo)
class PostVideoAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'video')
    list_filter = ('post__created_at',)
    search_fields = ('post__text',)

@admin.register(PostFile)
class PostFileAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'file', 'file_type')
    list_filter = ('file_type', 'post__created_at')
    search_fields = ('post__text',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'user', 'content', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'user__username', 'post__text')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
