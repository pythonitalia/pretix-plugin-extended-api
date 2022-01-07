from pretix.api.urls import event_router
from .views import TestViewSet

event_router.register('testapi', TestViewSet, basename='testapi')
