from django.db import models

# ---------------- EVENTS ----------------
class Event(models.Model):
    name = models.CharField(max_length=255, default="Untitled Event")
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="events/", blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-id"]
        verbose_name = "Event"
        verbose_name_plural = "Events"


# ---------------- VISITORS ----------------
class Visitor(models.Model):
    fname = models.CharField("Full Name", max_length=255, default="Unknown")
    mobile = models.CharField("Mobile Number", max_length=20, default="Unknown")
    email = models.EmailField("Email Address", max_length=255, default="Unknown")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.fname} - {self.mobile}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Visitor"
        verbose_name_plural = "Visitors"


# ---------------- VENUE ----------------
class VenueType(models.Model):
    VENUE_CHOICES = (
        ('marriage_hall','Marriage Hall'),
        ('banquet_hall','Banquet Hall'),
        ('openspace','Open Space'),
        ('conference_room','Conference Room'),
        ('traditional_mandapam','Traditional Mandapam'),
        ('others','Others'),
    )
    venue_type = models.CharField(max_length=255, choices=VENUE_CHOICES, default='others')
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='venue_types/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    area = models.CharField(max_length=255, blank=True, null=True)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Venue Type"
        verbose_name_plural = "Venue Types"


# ---------------- VENUE INVENTORY ----------------
class VenueRequisition(models.Model):
    venue = models.ForeignKey(VenueType, on_delete=models.CASCADE, related_name="inventories")
    
    tables_count = models.IntegerField(default=0)
    chairs_count = models.IntegerField(default=0)
    baloons_count = models.IntegerField(default=0)
    garlands_count = models.IntegerField(default=0)

    DECOR_CHOICES = (('basic','Basic'),('standard','Standard'),('premium','Premium'))
    SERVICE_CHOICES = (('none','None'),('basic','Basic'),('standard','Standard'),('premium','Premium'))

    decor_type = models.CharField(max_length=20, choices=DECOR_CHOICES, default='standard')
    band_type = models.CharField(max_length=20, choices=SERVICE_CHOICES, default='none')
    DJ_type = models.CharField(max_length=20, choices=SERVICE_CHOICES, default='none')

    class Meta:
        verbose_name = "Venue Inventory"
        verbose_name_plural = "Venue Inventories"

    def __str__(self):
        return f"{self.venue.name} Inventory"


# ---------------- REQUISITIONS ----------------
class Requisition(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="requisitions")
    visitor = models.ForeignKey(Visitor, on_delete=models.SET_NULL, null=True, blank=True, related_name="requisitions")
    visitor_name = models.CharField(max_length=255, default="Unknown")
    phone = models.CharField(max_length=20, default="Unknown")
    email = models.EmailField(default="unknown@example.com", blank=True)
    number_of_people = models.IntegerField(default=0)
    venue_type = models.CharField(max_length=255, blank=True, null=True)
    budget = models.CharField(max_length=255, blank=True, null=True)
    religious_affiliation = models.CharField(max_length=255, blank=True, null=True)
    special_requests = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Req #{self.id} — {self.event.name} — {self.visitor_name}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Requisition"
        verbose_name_plural = "Requisitions"

from django.db import models
from .models import Requisition

# ---------------- EXTRA REQUISITIONS ----------------
class ExtraRequisitions(models.Model):
    requisition = models.OneToOneField(Requisition, on_delete=models.CASCADE, related_name="extra_requisitions")

    # Numbers
    tables = models.IntegerField(default=0)
    chairs = models.IntegerField(default=0)
    baloons = models.IntegerField(default=0)
    garlands = models.IntegerField(default=0)

    # Service choices with images
    decor = models.CharField(
        max_length=20,
        choices=(("basic", "Basic"), ("standard", "Standard"), ("premium", "Premium")),
        default="standard"
    )
    decor_image_basic = models.ImageField(upload_to="extra_items/decor/", blank=True, null=True)
    decor_image_standard = models.ImageField(upload_to="extra_items/decor/", blank=True, null=True)
    decor_image_premium = models.ImageField(upload_to="extra_items/decor/", blank=True, null=True)

    band = models.CharField(
        max_length=20,
        choices=(("none", "None"), ("basic", "Basic"), ("standard", "Standard"), ("premium", "Premium")),
        default="none"
    )
    band_image_none = models.ImageField(upload_to="extra_items/band/", blank=True, null=True)
    band_image_basic = models.ImageField(upload_to="extra_items/band/", blank=True, null=True)
    band_image_standard = models.ImageField(upload_to="extra_items/band/", blank=True, null=True)
    band_image_premium = models.ImageField(upload_to="extra_items/band/", blank=True, null=True)

    DJ = models.CharField(
        max_length=20,
        choices=(("none", "None"), ("basic", "Basic"), ("standard", "Standard"), ("premium", "Premium")),
        default="none"
    )
    DJ_image_none = models.ImageField(upload_to="extra_items/dj/", blank=True, null=True)
    DJ_image_basic = models.ImageField(upload_to="extra_items/dj/", blank=True, null=True)
    DJ_image_standard = models.ImageField(upload_to="extra_items/dj/", blank=True, null=True)
    DJ_image_premium = models.ImageField(upload_to="extra_items/dj/", blank=True, null=True)

    # Previously boolean add-ons now services with images
    stereo = models.CharField(
        max_length=20,
        choices=(("none", "None"), ("basic", "Basic"), ("premium", "Premium")),
        default="none"
    )
    stereo_image_none = models.ImageField(upload_to="extra_items/stereo/", blank=True, null=True)
    stereo_image_basic = models.ImageField(upload_to="extra_items/stereo/", blank=True, null=True)
    stereo_image_premium = models.ImageField(upload_to="extra_items/stereo/", blank=True, null=True)

    lighting = models.CharField(
        max_length=20,
        choices=(("none", "None"), ("basic", "Basic"), ("premium", "Premium")),
        default="none"
    )
    lighting_image_none = models.ImageField(upload_to="extra_items/lighting/", blank=True, null=True)
    lighting_image_basic = models.ImageField(upload_to="extra_items/lighting/", blank=True, null=True)
    lighting_image_premium = models.ImageField(upload_to="extra_items/lighting/", blank=True, null=True)

    photography = models.CharField(
        max_length=20,
        choices=(("none", "None"), ("basic", "Basic"), ("premium", "Premium")),
        default="none"
    )
    photography_image_none = models.ImageField(upload_to="extra_items/photography/", blank=True, null=True)
    photography_image_basic = models.ImageField(upload_to="extra_items/photography/", blank=True, null=True)
    photography_image_premium = models.ImageField(upload_to="extra_items/photography/", blank=True, null=True)

    videography = models.CharField(
        max_length=20,
        choices=(("none", "None"), ("basic", "Basic"), ("premium", "Premium")),
        default="none"
    )
    videography_image_none = models.ImageField(upload_to="extra_items/videography/", blank=True, null=True)
    videography_image_basic = models.ImageField(upload_to="extra_items/videography/", blank=True, null=True)
    videography_image_premium = models.ImageField(upload_to="extra_items/videography/", blank=True, null=True)

    mic = models.CharField(
        max_length=20,
        choices=(("none", "None"), ("basic", "Basic"), ("premium", "Premium")),
        default="none"
    )
    mic_image_none = models.ImageField(upload_to="extra_items/mic/", blank=True, null=True)
    mic_image_basic = models.ImageField(upload_to="extra_items/mic/", blank=True, null=True)
    mic_image_premium = models.ImageField(upload_to="extra_items/mic/", blank=True, null=True)

    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def total_cost(self):
        # Implement pricing logic later
        return 0

    def __str__(self):
        return f"Extra requisitions for {self.requisition.visitor_name}"
