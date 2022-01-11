from pretix.api.urls import event_router

from .views.tickets import TicketsViewSet

event_router.register("tickets", TicketsViewSet, basename="tickets")
