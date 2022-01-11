import pytest
from pretix.base.models import Order

pytestmark = pytest.mark.django_db


def test_auth_required_to_check_if_email_has_ticket(client, event):
    resp = client.post(
        "/api/v1/organizers/dummy/events/dummy/tickets/attendee-has-ticket/"
    )
    assert resp.status_code == 401


def test_no_permissions_token_fails(no_permissions_token_client, event):
    resp = no_permissions_token_client.post(
        "/api/v1/organizers/dummy/events/dummy/tickets/attendee-has-ticket/"
    )
    assert resp.status_code == 403


def test_email_cannot_be_empty(token_client, event):
    resp = token_client.post(
        "/api/v1/organizers/dummy/events/dummy/tickets/attendee-has-ticket/",
        data={"attendee_email": "", "events": []},
        format="json",
    )

    assert resp.status_code == 400
    assert resp.data["attendee_email"][0].code == "blank"


def test_email_cannot_be_invalid(token_client, event):
    resp = token_client.post(
        "/api/v1/organizers/dummy/events/dummy/tickets/attendee-has-ticket/",
        data={"attendee_email": "SELECT id FROM sushi; --", "events": []},
        format="json",
    )

    assert resp.status_code == 400
    assert resp.data["attendee_email"][0].code == "invalid"


def test_email_has_tickets_with_no_events(token_client, event):
    resp = token_client.post(
        "/api/v1/organizers/dummy/events/dummy/tickets/attendee-has-ticket/",
        data={"attendee_email": "test@email.it", "events": []},
        format="json",
    )

    assert resp.status_code == 200
    assert resp.data["user_has_admission_ticket"] is False


def test_email_has_tickets(token_client, event, order):
    resp = token_client.post(
        "/api/v1/organizers/dummy/events/dummy/tickets/attendee-has-ticket/",
        data={
            "attendee_email": "test@email.it",
            "events": [{"organizer_slug": "dummy", "event_slug": "dummy"}],
        },
        format="json",
    )

    assert resp.status_code == 200
    assert resp.data["user_has_admission_ticket"] is True


def test_email_has_tickets_but_for_different_event(token_client, event, order):
    # order is for dummy, dummy
    resp = token_client.post(
        "/api/v1/organizers/dummy/events/dummy/tickets/attendee-has-ticket/",
        data={
            "attendee_email": "test@email.it",
            "events": [{"organizer_slug": "python-italia", "event_slug": "pycon-10"}],
        },
        format="json",
    )

    assert resp.status_code == 200
    assert resp.data["user_has_admission_ticket"] is False


def test_email_has_no_ticket(token_client, event, order):
    # order is for dummy, dummy
    resp = token_client.post(
        "/api/v1/organizers/dummy/events/dummy/tickets/attendee-has-ticket/",
        data={
            "attendee_email": "marco@noticket.it",
            "events": [{"organizer_slug": "dummy", "event_slug": "dummy"}],
        },
        format="json",
    )

    assert resp.status_code == 200
    assert resp.data["user_has_admission_ticket"] is False


def test_email_has_tickets_with_multiple_events_different_organizers(
    token_client, event, event2, order_event_2
):
    resp = token_client.post(
        "/api/v1/organizers/dummy/events/dummy/tickets/attendee-has-ticket/",
        data={
            "attendee_email": "test@email.it",
            "events": [
                {"organizer_slug": "dummy", "event_slug": "dummy"},
                {"organizer_slug": "python-italia", "event_slug": "smart"},
            ],
        },
        format="json",
    )

    assert resp.status_code == 200
    assert resp.data["user_has_admission_ticket"] is True


def test_email_has_order_but_no_admission_item(token_client, event, no_admission_order):
    resp = token_client.post(
        "/api/v1/organizers/dummy/events/dummy/tickets/attendee-has-ticket/",
        data={
            "attendee_email": "test@email.it",
            "events": [{"organizer_slug": "dummy", "event_slug": "dummy"}],
        },
        format="json",
    )

    assert resp.status_code == 200
    assert resp.data["user_has_admission_ticket"] is False


@pytest.mark.parametrize("order_status", (Order.STATUS_PENDING, Order.STATUS_EXPIRED, Order.STATUS_CANCELED))
def test_email_should_have_a_paid_order(token_client, event, order, order_status):
    order.status = order_status
    order.save()

    resp = token_client.post(
        "/api/v1/organizers/dummy/events/dummy/tickets/attendee-has-ticket/",
        data={
            "attendee_email": "test@email.it",
            "events": [{"organizer_slug": "dummy", "event_slug": "dummy"}],
        },
        format="json",
    )

    assert resp.status_code == 200
    assert resp.data["user_has_admission_ticket"] is False
