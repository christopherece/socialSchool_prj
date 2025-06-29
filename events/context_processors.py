from datetime import datetime, timedelta
from django.utils import timezone
from .models import Event

def upcoming_events(request):
    if request.user.is_authenticated:
        # Get events for the next 7 days
        today = timezone.now()
        next_week = today + timedelta(days=7)
        
        upcoming_events = Event.objects.filter(
            date__gte=today.date(),
            date__lte=next_week.date()
        ).order_by('date', 'time')[:5]
        
        return {
            'upcoming_events': upcoming_events
        }
    return {'upcoming_events': []}
