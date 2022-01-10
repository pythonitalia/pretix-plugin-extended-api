from django.db.models import Q
from pretix.base.models import Order, OrderPosition
from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


class EventMetadataBody(serializers.Serializer):
    organizer_slug = serializers.CharField(required=True)
    event_slug = serializers.CharField(required=True)


class AdmissionTicketBody(serializers.Serializer):
    attendee_email = serializers.EmailField(required=True)
    events = EventMetadataBody(many=True, required=True)


class AdmissionTicketViewSet(viewsets.ViewSet):
    @action(url_path="has-ticket", detail=False, methods=["post"])
    def attendee_has_ticket(self, request):
        serializer = AdmissionTicketBody(data=request.data)
        serializer.is_valid(True)

        attendee_email = serializer.data["attendee_email"]
        events = serializer.data["events"]

        if not events:
            return Response({"user_has_admission_ticket": False})

        qs = OrderPosition.objects.filter(
            attendee_email=attendee_email,
            order__status=Order.STATUS_PAID,
            item__admission=True,
        )

        events_filter = Q()
        for event in events:
            events_filter |= Q(
                order__event__slug=event["event_slug"],
                order__event__organizer__slug=event["organizer_slug"],
            )

        qs = qs.filter(events_filter)
        return Response({"user_has_admission_ticket": qs.exists()})
