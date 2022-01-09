from pretix.api.urls import router

from .views.admission_ticket import AdmissionTicketViewSet

router.register(
    "admission-tickets", AdmissionTicketViewSet, basename="admission-tickets"
)
