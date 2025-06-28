from django import forms
from django.forms.widgets import ClearableFileInput
from .models import Post, Comment

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleImageField(forms.ImageField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleFileInput(attrs={
            'multiple': True,
            'accept': 'image/*',
            'class': 'form-control-file'
        }))
        kwargs.setdefault('required', False)
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        if data:
            return super().clean(data, initial)
        return None

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleFileInput(attrs={
            'multiple': True,
            'class': 'form-control-file'
        }))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        if data:
            return super().clean(data, initial)
        return None

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Add a comment...'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].label = ''


class PostForm(forms.ModelForm):
    images = MultipleImageField(required=False)
    video = forms.FileField(required=False)
    files = MultipleFileField(required=False)
    
    class Meta:
        model = Post
        fields = ('text', 'media_type', 'images', 'video', 'files')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].widget.attrs.update({'class': 'form-control', 'rows': 3})
        self.fields['media_type'].widget.attrs.update({'class': 'form-control'})
        self.fields['images'].widget.attrs.update({'class': 'form-control-file', 'accept': 'image/*'})
        self.fields['video'].widget.attrs.update({'class': 'form-control-file'})
        self.fields['files'].widget.attrs.update({'class': 'form-control-file'})
        
    def clean_images(self):
        images = self.cleaned_data.get('images')
        if not images:
            return None
            
        # Check if there are too many images
        if len(images) > 5:
            raise forms.ValidationError('You can upload a maximum of 5 images.')
            
        # Check image size and format
            for image in images:
                if image.size > 5 * 1024 * 1024:  # 5MB max size
                    raise forms.ValidationError(f'Image {image.name} is too large. Maximum size is 5MB.')
                if not image.name.lower().endswith(('.png', '.jpg', '.jpeg')):
                    raise forms.ValidationError(f'Image {image.name} is not a valid image format. Only PNG, JPG, and JPEG are allowed.')
        return images
        
    def clean(self):
        cleaned_data = super().clean()
        media_type = cleaned_data.get('media_type')
        images = cleaned_data.get('images')
        video = cleaned_data.get('video')
        files = cleaned_data.get('files')
        
        # Validate required media based on media_type
        if media_type == 'image' and not images:
            self.add_error('images', 'Please select at least one image')
        elif media_type == 'video' and not video:
            self.add_error('video', 'Please select a video')
        elif media_type == 'file' and not files:
            self.add_error('files', 'Please select at least one file')
        elif media_type == 'mixed':
            if not any([images, video, files]):
                self.add_error('media_type', 'Please select at least one type of media')
        
        return cleaned_data

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.update({'class': 'form-control'})
