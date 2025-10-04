from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from .models import Event, Visitor, Requisition, ExtraRequisitions, VenueType, VenueRequisition
import json
from django.contrib.auth.decorators import login_required
# ---------------- CONSTANTS ----------------
NUMERIC_FIELDS = ["tables", "chairs", "baloons", "garlands"]
SERVICE_FIELDS = ["decor", "band", "DJ", "stereo", "lighting", "photography", "videography", "mic"]

# ---------------- HELPERS ----------------
def get_or_create_visitor(request):
    visitor_id = request.session.get("visitor_id")
    if visitor_id:
        visitor = Visitor.objects.filter(id=visitor_id).first()
        if visitor:
            return visitor
    visitor = Visitor.objects.create(fname="Guest", mobile="0000000000")
    request.session["visitor_id"] = visitor.id
    return visitor

def safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default

def get_extra_items(extra):
    return [
        {"id": "tables", "name": "Tables", "price": 50, "selected_quantity": extra.tables},
        {"id": "chairs", "name": "Chairs", "price": 10, "selected_quantity": extra.chairs},
        {"id": "baloons", "name": "Balloons", "price": 5, "selected_quantity": extra.baloons},
        {"id": "garlands", "name": "Garlands", "price": 20, "selected_quantity": extra.garlands},
        {"id": "decor", "name": "Decor", "price": 200, "selected_quantity": 1,
         "services": {"none": "None", "basic": "Basic", "standard": "Standard", "premium": "Premium"},
         "selected_service": extra.decor or "none"},
        {"id": "band", "name": "Band", "price": 300, "selected_quantity": 1,
         "services": {"none": "None", "basic": "Basic", "standard": "Standard", "premium": "Premium"},
         "selected_service": extra.band or "none"},
        {"id": "DJ", "name": "DJ", "price": 250, "selected_quantity": 1,
         "services": {"none": "None", "basic": "Basic", "standard": "Standard", "premium": "Premium"},
         "selected_service": extra.DJ or "none"},
        {"id": "stereo", "name": "Stereo", "price": 150, "selected_quantity": 1,
         "services": {"none": "None", "basic": "Basic", "premium": "Premium"},
         "selected_service": extra.stereo or "none"},
        {"id": "lighting", "name": "Lighting", "price": 100, "selected_quantity": 1,
         "services": {"none": "None", "basic": "Basic", "premium": "Premium"},
         "selected_service": extra.lighting or "none"},
        {"id": "photography", "name": "Photography", "price": 500, "selected_quantity": 1,
         "services": {"none": "None", "basic": "Basic", "premium": "Premium"},
         "selected_service": extra.photography or "none"},
        {"id": "videography", "name": "Videography", "price": 600, "selected_quantity": 1,
         "services": {"none": "None", "basic": "Basic", "premium": "Premium"},
         "selected_service": extra.videography or "none"},
        {"id": "mic", "name": "Mic", "price": 50, "selected_quantity": 1,
         "services": {"none": "None", "basic": "Basic", "premium": "Premium"},
         "selected_service": extra.mic or "none"},
    ]
# ---------------- EVENTS HOME ----------------
def events_home(request):
    events = Event.objects.all()
    visitor_id = request.session.get("visitor_id")
    show_popup = not visitor_id  # ✅ Show popup only if visitor not saved
    return render(request, "events/events_home.html", {
        "events": events,
        "show_popup": show_popup
    })


# ---------------- VISITOR POPUP SUBMIT ----------------
@csrf_exempt
def visitor_popup_submit(request):
    if request.method == "POST":
        fname = request.POST.get("fname")
        mobile = request.POST.get("mobile")

        if not fname or not mobile:
            return JsonResponse({
                "status": "error",
                "message": "Name and mobile are required"
            }, status=400)

        # ✅ Update or create visitor
        visitor, _ = Visitor.objects.update_or_create(
            mobile=mobile,
            defaults={"fname": fname}
        )

        # ✅ Save visitor in session
        request.session["visitor_id"] = visitor.id

        # ✅ Redirect to events_home again (so popup hides)
        return redirect("events:events_home")

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

# ---------------- VISITOR REQUISITION ----------------
def visitor_requisition(request):
    visitor = get_or_create_visitor(request)
    requisitions = Requisition.objects.filter(visitor=visitor).select_related("event")
    return render(request, "events/visitor_requisition.html", {"visitor": visitor, "requisitions": requisitions})

# ---------------- EVENT INFORMATION ----------------
def information_view(request, event_id):
    visitor = get_or_create_visitor(request)
    event = get_object_or_404(Event, id=event_id)
    request.session["current_event_id"] = event.id

    requisition, _ = Requisition.objects.get_or_create(visitor=visitor, event=event)

    if request.method == "POST":
        visitor_name = request.POST.get("visitor_name", visitor.fname)
        phone = request.POST.get("phone", visitor.mobile)
        email = request.POST.get("email", visitor.email or "unknown@example.com")
        visitor.fname = visitor_name
        visitor.mobile = phone
        visitor.email = email
        visitor.save()

        requisition.visitor_name = visitor_name
        requisition.phone = phone
        requisition.email = email
        requisition.number_of_people = safe_int(request.POST.get("number_of_people"))
        requisition.budget = request.POST.get("budget", "")
        requisition.religious_affiliation = request.POST.get("religious_affiliation", "")
        requisition.special_requests = request.POST.get("special_requests", "")
        requisition.venue_type = request.POST.get("venue_type", "")
        requisition.save()

        extra, _ = ExtraRequisitions.objects.get_or_create(requisition=requisition)
        for field in NUMERIC_FIELDS:
            setattr(extra, field, safe_int(request.POST.get(field)))
        for field in SERVICE_FIELDS:
            value = request.POST.get(field)
            if value:
                setattr(extra, field, value)
        extra.save()

        return redirect("events:venue_view")

    venues = VenueType.objects.all()
    extra, _ = ExtraRequisitions.objects.get_or_create(requisition=requisition)
    return render(request, "events/information.html", {
        "event": event,
        "venues": venues,
        "visitor": visitor,
        "requisition": requisition,
        "extra": extra
    })

# ---------------- VENUE VIEW ----------------
def venue_view(request):
    visitor = get_or_create_visitor(request)
    event_id = request.GET.get("event_id") or request.session.get("current_event_id")
    event = Event.objects.filter(id=event_id).first() if event_id else Event.objects.first()
    request.session["current_event_id"] = event.id

    venues = VenueType.objects.all()
    query = request.GET.get('q', '').strip()
    if query:
        venues = venues.filter(Q(name__icontains=query) | Q(location__icontains=query) | Q(area__icontains=query))

    requisition, _ = Requisition.objects.get_or_create(visitor=visitor, event=event)

    # Attach the selected venue object to requisition for template
    selected_venue = VenueType.objects.filter(name=requisition.venue_type).first()
    requisition.selected_venue = selected_venue

    # Venue inventory (optional, if needed in template/JS)
    venue_inventory = {}
    for venue in venues:
        inventories = []
        vr = VenueRequisition.objects.filter(venue=venue).first()
        if vr:
            inventories.extend([
                {"item_name": "Tables", "quantity": vr.tables_count},
                {"item_name": "Chairs", "quantity": vr.chairs_count},
                {"item_name": "Balloons", "quantity": vr.baloons_count},
                {"item_name": "Garlands", "quantity": vr.garlands_count},
                {"item_name": "Decor", "quantity": 1, "type": vr.decor_type},
                {"item_name": "Band", "quantity": 1, "type": vr.band_type},
                {"item_name": "DJ", "quantity": 1, "type": vr.DJ_type},
            ])
        extra, _ = ExtraRequisitions.objects.get_or_create(requisition=requisition)
        inventories.extend([
            {"item_name": f"Extra {field.capitalize()}", "quantity": getattr(extra, field), "type": getattr(extra, field, None)}
            for field in NUMERIC_FIELDS + SERVICE_FIELDS
        ])
        venue_inventory[venue.id] = inventories

    return render(request, "events/venues.html", {
        "venues": venues,
        "venue_inventory": json.dumps(venue_inventory),
        "requisition": requisition,
        "event": event
    })

# ---------------- SAVE SELECTED VENUE ----------------@csrf_exempt
def save_selected_venue(request):
    if request.method == "POST":
        data = json.loads(request.body)
        requisition = Requisition.objects.filter(id=data.get("requisition_id")).first()
        venue = VenueType.objects.filter(id=data.get("venue_id")).first()
        if not requisition or not venue:
            return JsonResponse({"status": "error", "message": "Invalid requisition or venue"}, status=400)

        # Save selected venue
        requisition.venue_type = venue.name
        requisition.save()

        # Return full venue info safely
        return JsonResponse({
            "status": "success",
            "venue_id": venue.id,
            "venue_name": venue.name,
            "discounted_price": getattr(venue, "discounted_price", 0),
            "lat": getattr(venue, "lat", 20.5937),  # default to India center if missing
            "lng": getattr(venue, "lng", 78.9629)
        })

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)
# ---------------- EXTRA REQUISITIONS ----------------
@csrf_exempt
def save_extra_requisition(request):
    if request.method == "POST":
        data = json.loads(request.body)
        requisition = Requisition.objects.filter(id=data.get("requisition_id")).first()
        if not requisition:
            return JsonResponse({"status": "error", "message": "Invalid requisition"}, status=400)

        extra, _ = ExtraRequisitions.objects.get_or_create(requisition=requisition)
        field_name = data.get("item_id")
        quantity = safe_int(data.get("quantity", 0))
        service_option = data.get("service_option", None)

        if field_name in NUMERIC_FIELDS:
            setattr(extra, field_name, quantity)
        elif field_name in SERVICE_FIELDS and service_option:
            setattr(extra, field_name, service_option)

        extra.save()
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

# ---------------- EXTRA REQUISITIONS VIEW ----------------
def extra_requisitions_view(request, requisition_id):
    requisition = get_object_or_404(Requisition, id=requisition_id)
    extra, _ = ExtraRequisitions.objects.get_or_create(requisition=requisition)
    selected_venue = VenueType.objects.filter(name=requisition.venue_type).first()
    extra_items = get_extra_items(extra)
    return render(request, "events/extra_requisitions.html", {
        "requisition": requisition,
        "extra": extra,
        "extra_items": extra_items,
        "selected_venue": selected_venue
    })

# ---------------- REQUISITIONS LIST ----------------
def requisitions_list(request):
    PSEUDO_PASS = "caller123"
    if not request.session.get("access_granted"):
        if request.method == "POST":
            if request.POST.get("password") == PSEUDO_PASS:
                request.session["access_granted"] = True
            else:
                return render(request, "events/requisitions.html", {"error": "Incorrect password.", "show_form": True})
        else:
            return render(request, "events/requisitions.html", {"show_form": True})
    requisitions = Requisition.objects.select_related("event", "visitor").prefetch_related("extra_requisitions").all()
    return render(request, "events/requisitions.html", {"requisitions": requisitions, "show_form": False})

# ---------------- STATIC PAGES ----------------
def about_view(request):
    return render(request, "about.html")

def services_view(request):
    return render(request, "services.html")

def contact_view(request):
    return render(request, "contact.html")

# ---------------- PAYMENT PAGE ----------------
def payment_page(request):
    visitor = get_or_create_visitor(request)
    event_id = request.session.get("current_event_id")
    event = get_object_or_404(Event, id=event_id)
    requisition, _ = Requisition.objects.get_or_create(visitor=visitor, event=event)
    extra, _ = ExtraRequisitions.objects.get_or_create(requisition=requisition)
    selected_venue = VenueType.objects.filter(name=requisition.venue_type).first()
    extra_items = get_extra_items(extra)

    numeric_fields = ["Tables", "Chairs", "Balloons", "Garlands"]  # Python list

    return render(request, "events/payment_page.html", {
        "visitor": visitor,
        "requisition": requisition,
        "extra": extra,
        "selected_venue": selected_venue,
        "extra_items": extra_items,
        "event": event,
        "numeric_fields": numeric_fields  # pass to template
    })
    
    
    
#-----------------Login View ----------------
@login_required
def login_redirect_view(request):
    return redirect('events:events_home')    
    
    
    
    
