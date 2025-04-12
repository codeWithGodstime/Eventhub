from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Event, EventRegistration
from .serializers import EventSerializers, EventRegistrationSerializers


class EventViewset(viewsets.ModelViewSet):
    serializer_class = EventSerializers.EventRetrieveSerializer
    queryset = Event.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        user = request.user
        serialized_data['organizer'] = user.id
        serialized_data = EventSerializers.EventCreateSerializer(data=request.data)
        serialized_data.is_valid(raise_exception=True)
        
        event = serialized_data.save()
        return Response(data=event.data, status=status.HTTP_201_CREATED)


class EventRegistrationViewset(viewsets.ModelViewSet):
    serializer_class = EventRegistrationSerializers.EventRegistrationRetrieveSerializer
    queryset = EventRegistration.objects.all()
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serialized_data = EventRegistrationSerializers.EventRegistrationCreateSerializer(data=request.data)
        serialized_data.is_valid(raise_exception=True)
        
        event = serialized_data.save()
        return Response(data=dict(message="Your registration was successful", data=event.data), status=status.HTTP_201_CREATED)


