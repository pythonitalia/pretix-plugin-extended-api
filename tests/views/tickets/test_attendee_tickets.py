import pytest

pytestmark = pytest.mark.django_db


def test_auth_required_to_get_attendee_tickets(client, event):
    resp = client.get("/api/v1/organizers/dummy/events/dummy/tickets/attendee-tickets/")
    assert resp.status_code == 401


def test_no_permissions_token_fails(no_permissions_token_client, event):
    resp = no_permissions_token_client.get(
        "/api/v1/organizers/dummy/events/dummy/tickets/attendee-tickets/"
    )
    assert resp.status_code == 403


def test_token_needs_ability_to_see_orders(token_client, team, event):
    team.can_view_orders = False
    team.save()

    resp = token_client.get(
        "/api/v1/organizers/dummy/events/dummy/tickets/attendee-tickets/"
    )
    assert resp.status_code == 403


def test_user_cannot_call_this_api(user_client, event):
    resp = user_client.get(
        "/api/v1/organizers/dummy/events/dummy/tickets/attendee-tickets/"
    )
    assert resp.status_code == 403


def test_email_cannot_be_empty(token_client, event):
    resp = token_client.get(
        "/api/v1/organizers/dummy/events/dummy/tickets/attendee-tickets/",
        data={"attendee_email": ""},
        format="json",
    )

    assert resp.status_code == 400
    assert resp.data["attendee_email"][0].code == "blank"


def test_email_cannot_be_invalid(token_client, event):
    resp = token_client.get(
        "/api/v1/organizers/dummy/events/dummy/tickets/attendee-tickets/",
        data={"attendee_email": "SELECT id FROM sushi; --"},
        format="json",
    )

    assert resp.status_code == 400
    assert resp.data["attendee_email"][0].code == "invalid"


def test_email_tickets(token_client, event, order):
    resp = token_client.get(
        "/api/v1/organizers/dummy/events/dummy/tickets/attendee-tickets/",
        data={
            "attendee_email": "test@email.it",
        },
        format="json",
    )

    assert resp.status_code == 200
    assert resp.data[0]["item"]["name"]["en"] == "Budget Ticket"
    assert resp.data[0]["price"] == "23.00"
    assert resp.data[0]["answers"][0]["question"]["question"]["en"] == "Tagline"
    assert resp.data[0]["answers"][0]["answer"] == "PySushi"
    assert (
        resp.data[0]["answers"][1]["question"]["question"]["en"]
        == "What do you want to eat?"
    )
    assert resp.data[0]["answers"][1]["answer"] == "Fiorentina"


def test_email_has_no_ticket(token_client, event, order):
    # order is for dummy, dummy
    resp = token_client.get(
        "/api/v1/organizers/dummy/events/dummy/tickets/attendee-tickets/",
        data={
            "attendee_email": "marco@noticket.it",
        },
        format="json",
    )

    assert resp.status_code == 200
    assert resp.data == []


def test_email_has_order_but_no_admission_item(token_client, event, no_admission_order):
    resp = token_client.get(
        "/api/v1/organizers/dummy/events/dummy/tickets/attendee-tickets/",
        data={
            "attendee_email": "test@email.it",
        },
        format="json",
    )

    assert resp.status_code == 200
    assert resp.data == []
