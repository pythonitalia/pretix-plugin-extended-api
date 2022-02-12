from pretix.api.urls import event_router

from .views.tickets import TicketsViewSet
from .views.orders import OrdersViewSet

event_router.register("tickets", TicketsViewSet, basename="tickets")
event_router.register("extended-orders", OrdersViewSet, basename="extended-orders")
