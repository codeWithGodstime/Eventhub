from django.db import models
from django.utils.translation import gettext_lazy as _


class GenderType(models.TextChoices):
    MALE = "MALE", _("Male")
    FEMALE = "FEMALE", _("Female")


class NotificationType(models.TextChoices):
    pass


class EventRegistrationStatusType(models.TextChoices):
    CANCELLED = "CANCELLED", _("CANCELLED")
    CONFIRMED = "CONFIRMED", _("CONFIRMED")