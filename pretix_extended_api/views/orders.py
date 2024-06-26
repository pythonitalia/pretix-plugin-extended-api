from pretix.api.serializers.order import OrderSerializer
from pretix.api.views.order import EventOrderViewSet
from rest_framework import viewsets
from rest_framework.response import Response

from .permissions import check_permission


class OrdersViewSet(viewsets.ViewSet):
    def retrieve(self, request, pk: str, **kwargs):
        check_permission(request, "can_view_orders")

        codes = pk.split(",")
        qs = EventOrderViewSet(request=request).get_queryset()
        orders = qs.filter(code__in=codes)

        serializer = OrderSerializer(
            instance=orders,
            many=True,
            context={
                "request": request,
                "event": request.event,
                "pdf_data": False,
                "include": [],
                "exclude": [],
            },
        )
        return Response(serializer.data)
