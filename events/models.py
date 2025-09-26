from django.db import models

class Event(models.Model):
    name = models.CharField(max_length=255, default="Untitled Event")
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='events/', blank=True, null=True)

    def __str__(self):
        return self.name


class Visitor(models.Model):
    fname = models.CharField(max_length=255, default="Unknown")
    mobile = models.CharField(max_length=20, default="Unknown")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.fname} - {self.mobile}"


class Requisition(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="requisitions")
    visitor = models.ForeignKey(Visitor, on_delete=models.SET_NULL, null=True, blank=True, related_name="requisitions")

    # snapshot of visitor
    visitor_name = models.CharField(max_length=255, default="Unknown")
    phone = models.CharField(max_length=20, default="Unknown")
    email = models.EmailField(default="unknown@example.com", blank=True)

    # requested items
    number_of_people = models.IntegerField(default=0)
    tables = models.IntegerField(default=0)
    chairs = models.IntegerField(default=0)
    balloons = models.IntegerField(default=0)
    garlands = models.IntegerField(default=0)
    stereo = models.BooleanField(default=False)
    mic = models.BooleanField(default=False)

    # other details
    venue_type = models.CharField(max_length=255, blank=True, null=True)
    budget = models.CharField(max_length=255, blank=True, null=True)
    religious_affiliation = models.CharField(max_length=255, blank=True, null=True)
    special_requests = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Req #{self.id} — {self.event.name} — {self.visitor_name}"
