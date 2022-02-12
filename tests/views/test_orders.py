import pytest
from django_scopes import scopes_disabled
from pretix.base.models import Order

pytestmark = pytest.mark.django_db


def test_get_order_data(token_client, event, order):
    order.status = Order.STATUS_PAID
    order.save()

    resp = token_client.get(
        f"/api/v1/organizers/dummy/events/dummy/extended-orders/{order.code}/",
        format="json",
    )

    assert resp.status_code == 200
    assert len(resp.data) == 1
    assert resp.data[0]["code"] == order.code
    assert resp.data[0]["status"] == Order.STATUS_PAID


@scopes_disabled()
def test_get_multiple_orders_data(token_client, event, order):
    order.status = Order.STATUS_PAID
    order.save()
    order_1 = Order.objects.get(id=order.id)

    order.pk = None
    order.code = "BAA"
    order.status = Order.STATUS_PENDING
    order.save()
    order_2 = Order.objects.get(id=order.id)

    resp = token_client.get(
        f"/api/v1/organizers/dummy/events/dummy/extended-orders/{order_1.code},{order_2.code}/",
        format="json",
    )

    assert resp.status_code == 200
    assert len(resp.data) == 2

    order_1_data = next((item for item in resp.data if item["code"] == order_1.code))

    order_2_data = next((item for item in resp.data if item["code"] == order_2.code))

    assert order_1_data["code"] == order_1.code
    assert order_1_data["status"] == Order.STATUS_PAID

    assert order_2_data["code"] == order_2.code
    assert order_2_data["status"] == Order.STATUS_PENDING


def test_with_not_existent_order_code(token_client, event, order):
    order.code = "FOO"
    order.status = Order.STATUS_PAID
    order.save()

    resp = token_client.get(
        f"/api/v1/organizers/dummy/events/dummy/extended-orders/ABCABC/",
        format="json",
    )

    assert resp.status_code == 200
    assert len(resp.data) == 0


def test_needs_permissions(no_permissions_token_client, event, order):
    order.code = "FOO"
    order.status = Order.STATUS_PAID
    order.save()

    resp = no_permissions_token_client.get(
        f"/api/v1/organizers/dummy/events/dummy/extended-orders/FOO/",
        format="json",
    )

    assert resp.status_code == 403


def test_user_token_is_not_allowed(user_client, event, order):
    order.code = "FOO"
    order.status = Order.STATUS_PAID
    order.save()

    resp = user_client.get(
        f"/api/v1/organizers/dummy/events/dummy/extended-orders/FOO/",
        format="json",
    )

    assert resp.status_code == 403


def test_needs_authentication(client, event, order):
    order.code = "FOO"
    order.status = Order.STATUS_PAID
    order.save()

    resp = client.get(
        f"/api/v1/organizers/dummy/events/dummy/extended-orders/FOO/",
        format="json",
    )

    assert resp.status_code == 401
