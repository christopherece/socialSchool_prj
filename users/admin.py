from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'bio')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email')
    fieldsets = (
        (None, {'fields': ('user', 'role', 'bio', 'profile_picture')}),
    )
