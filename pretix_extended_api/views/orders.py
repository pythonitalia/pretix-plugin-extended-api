from pretix.api.serializers.order import OrderSerializer
from pretix.api.views.order import OrderViewSet
from pretix.base.models import TeamAPIToken
from rest_framework import exceptions, viewsets
from rest_framework.response import Response


class OrdersViewSet(viewsets.ViewSet):
    def retrieve(self, request, pk: str, **kwargs):
        # Only allow Team API tokens to call this API.
        perm_holder = request.auth if isinstance(request.auth, TeamAPIToken) else None
        if not perm_holder or not perm_holder.has_event_permission(
            request.event.organizer, request.event, "can_view_orders"
        ):
            raise exceptions.PermissionDenied()

        codes = pk.split(",")
        qs = OrderViewSet(request=request).get_queryset()
        orders = qs.filter(code__in=codes)

        serializer = OrderSerializer(
            instance=orders,
            many=True,
            context={
                "request": request,
                "event": request.event,
            },
        )
        return Response(serializer.data)
