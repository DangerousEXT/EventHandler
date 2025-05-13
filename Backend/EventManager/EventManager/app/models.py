"""
Definition of models.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Profile(models.Model):
    ROLE_CHOICES = (
        ('participant', 'Participant'),
        ('organizer', 'Organizer'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='participant')

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class OrganizerRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
        default='pending'
    )

    def __str__(self):
        return f"{self.user.username} - Organizer Request ({self.status})"

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=200)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='events/', blank=True, null=True)

    def __str__(self):
        return self.title

class EventRegistration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'event')

    def __str__(self):
        return f"{self.user.username} - {self.event.title}"

class Item(models.Model):
    SPONSOR_CHOICES = (
        ('sponsor1', 'Sponsor 1'),
        ('sponsor2', 'Sponsor 2'),
        ('sponsor3', 'Sponsor 3'),
        ('sponsor4', 'Sponsor 4'),
    )
    MERCH_TYPE_CHOICES = (
        ('sweatshirt', 'Sweatshirt'),
        ('cap', 'Cap'),
        ('hoodie', 'Hoodie'),
        ('socks', 'Socks'),
        ('pants', 'Pants'),
        ('mug', 'Mug'),
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.PositiveIntegerField()  # Price in points
    sponsor = models.CharField(max_length=50, choices=SPONSOR_CHOICES)
    merch_type = models.CharField(max_length=50, choices=MERCH_TYPE_CHOICES)
    created_at = models.DateTimeField(default=timezone.now)
    image = models.ImageField(upload_to='items/', blank=True, null=True)

    def __str__(self):
        return f"{self.title} ({self.merch_type}) - {self.price} points"