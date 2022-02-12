from pretix.api.urls import event_router

from .views.orders import OrdersViewSet
from .views.tickets import TicketsViewSet

event_router.register("tickets", TicketsViewSet, basename="tickets")
event_router.register("extended-orders", OrdersViewSet, basename="extended-orders")
