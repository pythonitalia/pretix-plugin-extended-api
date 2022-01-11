from rest_framework import serializers


class EventBodySerializer(serializers.Serializer):
    organizer_slug = serializers.CharField(required=True)
    event_slug = serializers.CharField(required=True)


class AttendeeHasTicketBodySerializer(serializers.Serializer):
    attendee_email = serializers.EmailField(required=True)
    events = EventBodySerializer(many=True, required=True)
