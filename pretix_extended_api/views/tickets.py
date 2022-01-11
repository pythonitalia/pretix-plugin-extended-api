from django.db.models import Q
from pretix.base.models import Order, OrderPosition, TeamAPIToken
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django_scopes import scopes_disabled

from .serializers import AttendeeHasTicketBodySerializer


class TicketsViewSet(viewsets.ViewSet):
    # Disable scoping because we want to allow cross-organization checking
    # This allows us to do stuff like, you can attend PyCon Italia 2022
    # if you attended europython 2021
    @scopes_disabled()
    @action(url_path="attendee-has-ticket", detail=False, methods=["post"])
    def attendee_has_ticket(self, request, **kwargs):
        # Only allow Team API tokens to call this API.
        perm_holder = request.auth if isinstance(request.auth, TeamAPIToken) else None
        if not perm_holder or not perm_holder.has_event_permission(request.event.organizer, request.event, 'can_view_orders'):
            raise PermissionError()

        serializer = AttendeeHasTicketBodySerializer(data=request.data)
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
