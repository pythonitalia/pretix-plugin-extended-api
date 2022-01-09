import pytest

pytestmark = pytest.mark.django_db


def test_view(token_client, event):
    resp = token_client.get("/api/v1/organizers/dummy/events/dummy/testapi/")
    assert resp.status_code == 200
    assert resp.json() == ["dummy", "dummy"]
