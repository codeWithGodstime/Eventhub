from django.db import models
from django_countries.fields import CountryField
from django.contrib.auth import get_user_model
from django.conf import settings
from utilities.utils import BaseModelMixin
from utilities.choices import EventRegistrationStatusType

User = get_user_model()


class Event(BaseModelMixin):
    title = models.CharField(max_length=200)
    date = models.DateField()
    time = models.TimeField(null=True, blank=True)
    description = models.TextField()
    short_description = models.TextField()
    organizer = models.ForeignKey(User, on_delete=models.CASCADE)
    is_paid = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    city = models.CharField(max_length=150)
    country = CountryField()
    slot = models.PositiveIntegerField()

    @property
    def link_uri(self):
        return f"{settings.FRONTEND_HOST_URL}/register/events/{self.id}"


class EventRegistration:
    name = models.CharField(max_length=200)
    email = models.EmailField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="event_registrations")
    status = models.CharField(max_length=10, choices=EventRegistrationStatusType.choices)
