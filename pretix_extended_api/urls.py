from pretix.api.urls import router

from .views.admission_tickets import AdmissionTicketsViewSet

router.register(
    "admission-tickets", AdmissionTicketsViewSet, basename="admission-tickets"
)
