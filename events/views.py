from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from .models import Event
from .forms import EventForm

def is_admin_or_teacher(user):
    return user.role in ['admin', 'teacher']

@login_required
@user_passes_test(is_admin_or_teacher)
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, 'Event created successfully!')
            return redirect('events:list')
    else:
        form = EventForm()
    return render(request, 'events/create_event.html', {'form': form})

@login_required
def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    return render(request, 'events/event_detail.html', {'event': event})

@login_required
def event_list(request):
    today = timezone.now().date()
    upcoming_events = Event.objects.filter(date__gte=today).order_by('date', 'time')
    return render(request, 'events/event_list.html', {
        'upcoming_events': upcoming_events,
        'today': today
    })
