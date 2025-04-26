"""
Definition of models.
"""

from django.db import models
from django.contrib.auth.models import User

class Event(models.Model):
    category = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    description = models.TextField()
    date_time = models.DateTimeField()
    image = models.ImageField(upload_to='events/', blank=True, null=True)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
