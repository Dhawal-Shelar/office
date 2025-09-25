from django.shortcuts import render, redirect, get_object_or_404
from .models import Event, Venue, Visitor

# Home page: list all events
def events_home(request):
    events = Event.objects.prefetch_related('venues').all()
    return render(request, 'events_home.html', {'events': events})

# Visitor login for a specific event
def visitor_login(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        mobile = request.POST.get('mobile')
        email = request.POST.get('email')
        if fname and lname and mobile and email:
            Visitor.objects.create(
                event=event,
                fname=fname,
                lname=lname,
                mobile=mobile,
                email=email
            )
            return redirect('venue_view', event_id=event.id)
    return render(request, 'login.html', {'event': event})

# Show venues for the specific event
def venue_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    venues = event.venues.all()
    return render(request, 'venues.html', {'event': event, 'venues': venues})
