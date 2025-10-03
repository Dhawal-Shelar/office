from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from .models import Event, Visitor, Requisition, ExtraRequisitions, VenueType, VenueRequisition
import json

# ---------------- EVENTS HOME ----------------
def events_home(request):
    events = Event.objects.all()
    visitor_id = request.session.get("visitor_id")
    show_popup = not visitor_id  # show modal if visitor not in session
    return render(request, "events_home.html", {"events": events, "show_popup": show_popup})

# ---------------- VISITOR POPUP ----------------
@csrf_exempt
def visitor_popup_submit(request):
    if request.method == "POST":
        fname = request.POST.get("fname")
        mobile = request.POST.get("mobile")
        if not fname or not mobile:
            return JsonResponse({"status": "error", "message": "Name and mobile are required"}, status=400)

        visitor, _ = Visitor.objects.update_or_create(fname=fname, mobile=mobile)
        request.session["visitor_id"] = visitor.id
        return JsonResponse({"status": "success", "redirect": "/visitor-requisition/"})

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

# ---------------- VISITOR REQUISITION ----------------
def visitor_requisition(request):
    visitor_id = request.session.get("visitor_id")
    if not visitor_id:
        return redirect("events_home")

    visitor = get_object_or_404(Visitor, id=visitor_id)
    requisitions = Requisition.objects.filter(visitor=visitor).select_related("event")
    return render(request, "visitor_requisition.html", {"visitor": visitor, "requisitions": requisitions})

# ---------------- EVENT INFORMATION ----------------
def information_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    visitor_id = request.session.get("visitor_id")
    visitor = Visitor.objects.filter(id=visitor_id).first()

    if not visitor:
        visitor = Visitor.objects.create(fname="Guest", mobile="0000000000")
        request.session["visitor_id"] = visitor.id

    request.session["current_event_id"] = event.id  # Save current event for payment page

    if request.method == "POST":
        # Safe helper for integer conversion
        def safe_int(value, default=0):
            try:
                return int(value)
            except (TypeError, ValueError):
                return default

        visitor_name = request.POST.get("visitor_name", visitor.fname)
        phone = request.POST.get("phone", visitor.mobile)
        email = request.POST.get("email", visitor.email or "unknown@example.com")

        visitor.fname = visitor_name
        visitor.mobile = phone
        visitor.email = email
        visitor.save()

        requisition_id = request.POST.get("requisition_id")
        number_of_people = safe_int(request.POST.get("number_of_people"))
        budget = request.POST.get("budget", "")
        religious_affiliation = request.POST.get("religious_affiliation", "")
        special_requests = request.POST.get("special_requests", "")
        venue_type = request.POST.get("venue_type", "")

        if requisition_id and requisition_id.isdigit():
            requisition, _ = Requisition.objects.update_or_create(
                id=int(requisition_id),
                defaults={
                    "event": event,
                    "visitor": visitor,
                    "visitor_name": visitor_name,
                    "phone": phone,
                    "email": email,
                    "number_of_people": number_of_people,
                    "budget": budget,
                    "religious_affiliation": religious_affiliation,
                    "special_requests": special_requests,
                    "venue_type": venue_type,
                }
            )
        else:
            requisition, _ = Requisition.objects.update_or_create(
                visitor=visitor,
                event=event,
                defaults={
                    "visitor_name": visitor_name,
                    "phone": phone,
                    "email": email,
                    "number_of_people": number_of_people,
                    "budget": budget,
                    "religious_affiliation": religious_affiliation,
                    "special_requests": special_requests,
                    "venue_type": venue_type,
                }
            )

        # Save extra requisitions
        extra, _ = ExtraRequisitions.objects.get_or_create(requisition=requisition)
        numeric_fields = ["tables", "chairs", "baloons", "garlands"]
        service_fields = ["decor", "band", "DJ", "stereo", "lighting", "photography", "videography", "mic"]

        for field in numeric_fields:
            value = safe_int(request.POST.get(field))
            setattr(extra, field, value)
        for field in service_fields:
            value = request.POST.get(field)
            if value:
                setattr(extra, field, value)
        extra.save()

        # Redirect to payment page
        return redirect("payment_page")

    # GET request
    requisition = Requisition.objects.filter(visitor=visitor, event=event).last()
    if not requisition:
        requisition = Requisition.objects.create(visitor=visitor, event=event)

    venues = VenueType.objects.all()
    return render(request, "information.html", {
        "event": event,
        "venues": venues,
        "visitor": visitor,
        "requisition": requisition,
    })

# ---------------- VENUE VIEW ----------------
def venue_view(request):
    visitor_id = request.session.get("visitor_id")
    visitor = Visitor.objects.filter(id=visitor_id).first() if visitor_id else None
    if not visitor:
        visitor = Visitor.objects.create(fname="Guest", mobile="0000000000")
        request.session["visitor_id"] = visitor.id

    event_id = request.GET.get("event_id") or request.session.get("current_event_id")
    event = Event.objects.filter(id=event_id).first() if event_id else Event.objects.first()
    request.session["current_event_id"] = event.id

    venues = VenueType.objects.all()
    query = request.GET.get('q', '').strip()
    if query:
        venues = venues.filter(Q(name__icontains=query) | Q(location__icontains=query) | Q(area__icontains=query))

    requisition = Requisition.objects.filter(visitor=visitor, event=event).last()
    if not requisition:
        requisition = Requisition.objects.create(visitor=visitor, event=event)

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
            {"item_name": "Extra Tables", "quantity": extra.tables},
            {"item_name": "Extra Chairs", "quantity": extra.chairs},
            {"item_name": "Extra Balloons", "quantity": extra.baloons},
            {"item_name": "Extra Garlands", "quantity": extra.garlands},
            {"item_name": "Extra Decor", "type": extra.decor, "quantity": 1},
            {"item_name": "Extra Band", "type": extra.band, "quantity": 1},
            {"item_name": "Extra DJ", "type": extra.DJ, "quantity": 1},
            {"item_name": "Extra Stereo", "type": extra.stereo, "quantity": 1},
            {"item_name": "Extra Lighting", "type": extra.lighting, "quantity": 1},
            {"item_name": "Extra Photography", "type": extra.photography, "quantity": 1},
            {"item_name": "Extra Videography", "type": extra.videography, "quantity": 1},
            {"item_name": "Extra Mic", "type": extra.mic, "quantity": 1},
        ])
        venue_inventory[venue.id] = inventories

    return render(request, "venues.html", {
        "venues": venues,
        "venue_inventory": json.dumps(venue_inventory),
        "requisition": requisition,
        "event": event,
    })

# ---------------- SAVE SELECTED VENUE ----------------
@csrf_exempt
def save_selected_venue(request):
    if request.method == "POST":
        data = json.loads(request.body)
        print("data",data)
        requisition_id = data.get("requisition_id")
        venue_id = data.get("venue_id")

        requisition = Requisition.objects.filter(id=requisition_id).first()
        venue = VenueType.objects.filter(id=venue_id).first()
        if not requisition or not venue:
            return JsonResponse({"status": "error", "message": "Invalid requisition or venue"}, status=400)

        requisition.venue_type = venue.name
        requisition.save()

        return JsonResponse({
            "status": "success",
            "venue_id": venue.id,
            "venue_name": venue.name,
            "discounted_price": venue.discounted_price
        })

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

# ---------------- EXTRA REQUISITIONS ----------------
@csrf_exempt
def save_extra_requisition(request):
    if request.method == "POST":
        data = json.loads(request.body)
        requisition_id = data.get("requisition_id")
        item_id = data.get("item_id")
        quantity = data.get("quantity", 0)
        service_option = data.get("service_option", None)

        requisition = Requisition.objects.filter(id=requisition_id).first()
        if not requisition:
            return JsonResponse({"status": "error", "message": "Invalid requisition"}, status=400)

        extra, _ = ExtraRequisitions.objects.get_or_create(requisition=requisition)

        item_map = {
            "tables": "tables",
            "chairs": "chairs",
            "baloons": "baloons",
            "garlands": "garlands",
            "decor": "decor",
            "band": "band",
            "DJ": "DJ",
            "stereo": "stereo",
            "lighting": "lighting",
            "photography": "photography",
            "videography": "videography",
            "mic": "mic",
        }

        field_name = item_map.get(str(item_id))
        if not field_name:
            return JsonResponse({"status": "error", "message": "Invalid item"}, status=400)

        if field_name in ["tables", "chairs", "baloons", "garlands"]:
            setattr(extra, field_name, int(quantity))
        else:
            if service_option:
                setattr(extra, field_name, service_option)

        extra.save()
        return JsonResponse({"status": "success"})

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

# ---------------- EXTRA REQUISITIONS VIEW ----------------
def extra_requisitions_view(request, requisition_id):
    requisition = get_object_or_404(Requisition, id=requisition_id)
    extra, _ = ExtraRequisitions.objects.get_or_create(requisition=requisition)
    selected_venue = VenueType.objects.filter(name=requisition.venue_type).first()

    extra_items = [
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

    return render(request, "extra_requisitions.html", {
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
            password = request.POST.get("password", "")
            if password == PSEUDO_PASS:
                request.session["access_granted"] = True
            else:
                return render(request, "requisitions.html", {"error": "Incorrect password.", "show_form": True})
        else:
            return render(request, "requisitions.html", {"show_form": True})

    requisitions = Requisition.objects.select_related("event", "visitor").prefetch_related("extra_requisitions").all()
    return render(request, "requisitions.html", {"requisitions": requisitions, "show_form": False})

# ---------------- STATIC PAGES ----------------
def about_view(request):
    return render(request, "about.html")

def services_view(request):
    return render(request, "services.html")

def contact_view(request):
    return render(request, "contact.html")

# ---------------- PAYMENT PAGE ----------------
def payment_page(request):
    visitor_id = request.session.get("visitor_id")
    event_id = request.session.get("current_event_id")
    if not visitor_id or not event_id:
        return redirect("events_home")

    visitor = get_object_or_404(Visitor, id=visitor_id)
    event = get_object_or_404(Event, id=event_id)

    requisition = Requisition.objects.filter(visitor=visitor, event=event).last()
    if not requisition:
        requisition = Requisition.objects.create(visitor=visitor, event=event)

    extra, _ = ExtraRequisitions.objects.get_or_create(requisition=requisition)

    # Get selected venue object
    selected_venue = VenueType.objects.filter(name=requisition.venue_type).first()

    # Prepare extra_items for display on payment page (similar to extra_requisitions)
    extra_items = [
    {"id": "tables", "name": "Tables", "price": 50, "selected_quantity": extra.tables},
    {"id": "chairs", "name": "Chairs", "price": 10, "selected_quantity": extra.chairs},
    {"id": "baloons", "name": "Balloons", "price": 5, "selected_quantity": extra.baloons},
    {"id": "garlands", "name": "Garlands", "price": 20, "selected_quantity": extra.garlands},

    {"id": "decor", "name": "Decor", "price": 200, "selected_quantity": 1,
     "services": {"basic": "Basic", "standard": "Standard", "premium": "Premium"},
     "selected_service": extra.decor},

    {"id": "band", "name": "Band", "price": 300, "selected_quantity": 1,
     "services": {"none": "None", "basic": "Basic", "standard": "Standard", "premium": "Premium"},
     "selected_service": extra.band},

    {"id": "DJ", "name": "DJ", "price": 250, "selected_quantity": 1,
     "services": {"none": "None", "basic": "Basic", "standard": "Standard", "premium": "Premium"},
     "selected_service": extra.DJ},

    {"id": "stereo", "name": "Stereo", "price": 150, "selected_quantity": 1,
     "services": {"none": "None", "basic": "Basic", "premium": "Premium"},
     "selected_service": extra.stereo},

    {"id": "lighting", "name": "Lighting", "price": 100, "selected_quantity": 1,
     "services": {"none": "None", "basic": "Basic", "premium": "Premium"},
     "selected_service": extra.lighting},

    {"id": "photography", "name": "Photography", "price": 500, "selected_quantity": 1,
     "services": {"none": "None", "basic": "Basic", "premium": "Premium"},
     "selected_service": extra.photography},

    {"id": "videography", "name": "Videography", "price": 600, "selected_quantity": 1,
     "services": {"none": "None", "basic": "Basic", "premium": "Premium"},
     "selected_service": extra.videography},

    {"id": "mic", "name": "Mic", "price": 50, "selected_quantity": 1,
     "services": {"none": "None", "basic": "Basic", "premium": "Premium"},
     "selected_service": extra.mic},
    ]

    return render(request, "payment_page.html", {
        "visitor": visitor,
        "requisition": requisition,
        "extra": extra,
        "selected_venue": selected_venue,
        "extra_items": extra_items,
        "event": event,
    })