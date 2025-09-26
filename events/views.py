from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Event, Visitor, Requisition

def events_home(request):
    events = Event.objects.all()
    show_popup = not bool(request.session.get('visitor_id'))

    return render(request, 'events_home.html', {
        'events': events,
        'show_popup': show_popup,
    })


def visitor_popup_submit(request):
    if request.method == "POST":
        fname = request.POST.get('fname', '').strip()
        mobile = request.POST.get('mobile', '').strip()

        if not (fname and mobile):
            messages.error(request, "Please provide both name and mobile.")
            return redirect('events_home')

        visitor, created = Visitor.objects.get_or_create(mobile=mobile, defaults={'fname': fname})

        if not created and visitor.fname != fname:
            visitor.fname = fname
            visitor.save()

        # Save visitor info in session
        request.session['visitor_id'] = visitor.id
        request.session['visitor_name'] = visitor.fname
        request.session['visitor_mobile'] = visitor.mobile

    return redirect('events_home')


def information_view(request, event_id):
    event = Event.objects.get(id=event_id)

    if request.method == "POST":
        Requisition.objects.create(
            event=event,
            visitor_name=request.POST.get("visitor_name"),
            phone=request.POST.get("phone"),
            email=request.POST.get("email"),
            number_of_people=request.POST.get("number_of_people"),
            tables=request.POST.get("tables"),
            chairs=request.POST.get("chairs"),
            balloons=request.POST.get("balloons"),
            garlands=request.POST.get("garlands"),
            stereo=request.POST.get("stereo"),
            mic=request.POST.get("mic"),
            venue_type=request.POST.get("venue_type"),
            budget=request.POST.get("budget"),
            religious_affiliation=request.POST.get("religious_affiliation"),
            special_requests=request.POST.get("special_requests")
        )
        messages.success(request, "Your request has been submitted!")
        return redirect('events_home')

    return render(request, 'information.html', {'event': event})


def requisitions_list(request):
    requisitions = Requisition.objects.select_related('event', 'visitor').order_by('-created_at')
    return render(request, 'requisitions.html', {'requisitions': requisitions})


# Static pages
def about_view(request):
    event = Event.objects.all()
    team_members = [
        {"name": "Alice Johnson", "role": "Event Planner", "image": "https://i.pravatar.cc/150?img=32"},
        {"name": "Bob Smith", "role": "Coordinator", "image": "https://i.pravatar.cc/150?img=45"},
        {"name": "Catherine Lee", "role": "Marketing", "image": "https://i.pravatar.cc/150?img=12"},
    ]
    return render(request, 'about.html', {"team_members": team_members, 'event': event})


def services_view(request):
    event = Event.objects.all()
    services = [
        
        {"title": "Wedding Planning", "icon": "bi-heart-fill", "description": "Complete wedding planning solutions."},
        {"title": "Corporate Events", "icon": "bi-briefcase-fill", "description": "Professional corporate events management."},
        {"title": "Birthday Parties", "icon": "bi-cup-straw", "description": "Fun and customized birthday events."},
        {"title": "Conference & Seminars", "icon": "bi-mic", "description": "Organize conferences and seminars smoothly."},
    ]
    return render(request, 'services.html', {"services": services, 'event':event})


def contact_view(request):
    event = Event.objects.all()
    if request.method == "POST":
        # Optionally store contact messages
        request.session['contact_success'] = True
        return redirect('contact')

    contact_success = request.session.pop('contact_success', False)
    return render(request, 'contact.html', {"contact_success": contact_success , 'event': event})
