from django.db import models

class Event(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)

    def __str__(self):
        return self.name

class Venue(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='venues')
    venue_name = models.CharField(max_length=100)
    location = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='venue_images/', blank=True, null=True)

    def __str__(self):
        return f"{self.venue_name} ({self.event.name})"

class Visitor(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='visitors')
    fname = models.CharField(max_length=50)
    lname = models.CharField(max_length=50)
    mobile = models.CharField(max_length=15)
    email = models.EmailField(max_length=100)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.fname} {self.lname} - {self.event.name}"
