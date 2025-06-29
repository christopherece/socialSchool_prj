from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class Event(models.Model):
    EVENT_TYPES = (
        ('lecture', _('Lecture')),
        ('workshop', _('Workshop')),
        ('exam', _('Exam')),
        ('other', _('Other')),
    )

    title = models.CharField(_('title'), max_length=200)
    description = models.TextField(_('description'))
    date = models.DateField(_('date'))
    time = models.TimeField(_('time'))
    location = models.CharField(_('location'), max_length=200)
    event_type = models.CharField(_('type'), max_length=20, choices=EVENT_TYPES)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('created by'),
        related_name='created_events'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('event')
        verbose_name_plural = _('events')
        ordering = ['-date', '-time']
        
    def __str__(self):
        return self.title

    def is_upcoming(self):
        return self.date >= timezone.now().date()

    def is_today(self):
        return self.date == timezone.now().date()
