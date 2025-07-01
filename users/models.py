from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class CustomUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='custom_user')
    ROLE_CHOICES = (
        ('student', _('Student')),
        ('teacher', _('Teacher')),
        ('admin', _('Administrator')),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
    
    def __str__(self):
        return self.user.username
