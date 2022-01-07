from rest_framework.response import Response
from rest_framework import viewsets


class TestViewSet(viewsets.ViewSet):
    def list(self, request, organizer, event):
        return Response([
            organizer,
            event
        ])
