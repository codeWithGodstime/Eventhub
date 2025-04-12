from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import EventViewset

router = DefaultRouter()
router.register("", EventViewset, basename="events")

urlpatterns = router.urls