
from rest_framework import viewsets, serializers
from rest_framework.response import Response
from rest_framework.decorators import action
from pretix.base.models import OrderPosition, Order
from django.db.models import Q
from functools import reduce
from operator import or_
class EventMetadataBody(serializers.Serializer):
    organizer_slug = serializers.CharField(required=True)
    event_slug = serializers.CharField(required=True)


class AdmissionTicketBody(serializers.Serializer):
    attendee_email = serializers.EmailField(required=True)
    events = EventMetadataBody(many=True, required=True)


class AdmissionTicketViewSet(viewsets.ViewSet):
    @action(url_path='attendee-ticket', detail=False, methods=['post'])
    def attendee_ticket(self, request):
        serializer = AdmissionTicketBody(data=request.data)
        serializer.is_valid(True)

        attendee_email = serializer.data['attendee_email']
        events = serializer.data['events']

        if not events:
            return Response({
                "user_has_admission_ticket": False
            })

        qs = OrderPosition.objects.filter(
            attendee_email=attendee_email,
            order__status=Order.STATUS_PAID,
            item__admission=True,
        )

        events_filter = reduce(
            or_, [Q(order__event__slug=event['event_slug'],
                    order__event__organizer__slug=event['organizer_slug']) for event in events]
        )
        qs = qs.filter(events_filter)
        return Response({
            "user_has_admission_ticket": qs.exists()
        })
