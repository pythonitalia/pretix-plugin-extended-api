import pytest
pytestmark = pytest.mark.django_db


def test_view(token_client, event):
    # put your first tests here
    # /api/v1/organizers/test/events/event/testapi/
    # http://localhost:8000/api/v1/organizers/test/events/test-event/testapi/
    resp = token_client.get('/api/v1/organizers/dummy/events/dummy/testapi/')
    assert resp.status_code == 200
