from rest_framework import serializers
from .models import Event, EventRegistration


class EventSerializers:
    class EventCreateSerializer(serializers.ModelSerializers):
        class Meta:
            model = Event
            fields = (
                "title",
                "date",
                "time",
                "description",
                "short_description",
                "organizer",
                "is_paid",
                "price",
                "city",
                "country",
                "slot"
            )

    
    class EventRetrieveSerializer(serializers.ModelSerializers):
        share_url = serializers.CharField(source='link_uri')

        class Meta:
            model = Event
            fields = (
                "id",
                "title",
                "date",
                "time",
                "description",
                "short_description",
                "organizer",
                "is_paid",
                "price",
                "city",
                "country",
                "slot",
                "share_url",
                "created_at"
            )


class EventRegistrationSerializers:
    class EventRegistrationCreateSerializer(serializers.ModelSerializer):
        class Meta:
            model = EventRegistration
            fields = (
                "name", 
                "email",
                "event",
            )

    class EventRegistrationRetrieveSerializer(serializers.ModelSerializer):
        class Meta:
            model = EventRegistration
            fields = (
                "id",
                "name", 
                "email",
                "event",
                "status",
                "created_at"
            )