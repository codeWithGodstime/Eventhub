from django.contrib.gis.db import models
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django_countries.fields import CountryField
from user.manager import CustomUserManager
from utilities.utils import BaseModelMixin
from utilities.choices import GenderType, NotificationType


class User(BaseModelMixin, AbstractUser):

    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=300, blank=False, null=False)
    last_name = models.CharField(max_length=300, blank=False, null=False)
    username = models.CharField(max_length=50, unique=True, null=True, blank=True)

    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    gender = models.CharField(max_length=10, choices=GenderType.choices, null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = CustomUserManager()

    class Meta:
        ordering = ["-created_at"]

    @property
    def fullname(self):
        return f"{self.first_name} {self.last_name}"

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(
            subject,
            message,
            from_email,
            [self.email],
            fail_silently=True,
            **kwargs,
        )


class Notification(BaseModelMixin):
    receiver = models.ForeignKey("User", on_delete=models.CASCADE, related_name='notification_receiver')
    type = models.CharField(max_length=20, choices=NotificationType.choices)
    is_read = models.BooleanField(default=False)
    metadata = models.JSONField(blank=True, null=True, default=dict)
    """e.g
    {
     message: "John just arrivend in akwa reach out to him"
     sender_profile_link: mesh.com/john
    }
    """

class NotificationPreference(BaseModelMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notification_preference")
    receive_email_notification_about_own_events = models.BooleanField(default=True)
    receiver_marketing_email = models.BooleanField(default=False)
    receive_registration_notifications = models.BooleanField(default=True)
    receive_event_reminders = models.BooleanField(default=True) 


class SubscriptionPlan(BaseModelMixin):
    pass


