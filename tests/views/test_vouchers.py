from datetime import timedelta
from django.utils import timezone
import pytest

pytestmark = pytest.mark.django_db


def test_voucher_info_for_item(token_client, admission_item, voucher_for_item):
    resp = token_client.get(
        f"/api/v1/organizers/dummy/events/dummy/extended-vouchers/{voucher_for_item.code}/",
        format="json",
    )

    assert resp.status_code == 200
    assert resp.data["id"] == voucher_for_item.id
    assert resp.data["item"] == admission_item.id
    assert resp.data["quota"] is None
    assert resp.data["quota_items"] is None


def test_quota_voucher_info(token_client, admission_item, quota, voucher_for_quota):
    resp = token_client.get(
        f"/api/v1/organizers/dummy/events/dummy/extended-vouchers/{voucher_for_quota.code}/",
        format="json",
    )

    assert resp.status_code == 200
    assert resp.data["id"] == voucher_for_quota.id
    assert resp.data["item"] is None
    assert resp.data["quota"] == quota.id
    assert resp.data["quota_items"] == [admission_item.id]


def test_voucher_for_all_items(token_client, voucher_for_all_items):
    resp = token_client.get(
        f"/api/v1/organizers/dummy/events/dummy/extended-vouchers/{voucher_for_all_items.code}/",
        format="json",
    )

    assert resp.status_code == 200
    assert resp.data["id"] == voucher_for_all_items.id
    assert resp.data["item"] is None
    assert resp.data["quota"] is None
    assert resp.data["quota_items"] is None


def test_invalid_code(token_client, voucher_for_all_items):
    resp = token_client.get(
        "/api/v1/organizers/dummy/events/dummy/extended-vouchers/ABCABCABC/",
        format="json",
    )

    assert resp.status_code == 404
    assert resp.data is None


def test_requires_authentication(client, voucher_for_all_items):
    resp = client.get(
        f"/api/v1/organizers/dummy/events/dummy/extended-vouchers/{voucher_for_all_items.code}/",
        format="json",
    )

    assert resp.status_code == 401


def test_requires_authentication_of_team(user_client, voucher_for_all_items):
    resp = user_client.get(
        f"/api/v1/organizers/dummy/events/dummy/extended-vouchers/{voucher_for_all_items.code}/",
        format="json",
    )

    assert resp.status_code == 403


def test_requires_permissions(no_permissions_token_client, voucher_for_all_items):
    resp = no_permissions_token_client.get(
        f"/api/v1/organizers/dummy/events/dummy/extended-vouchers/{voucher_for_all_items.code}/",
        format="json",
    )

    assert resp.status_code == 403


def test_expired_voucher_is_not_returned(token_client, voucher_for_item):
    voucher_for_item.valid_until = timezone.now() - timedelta(days=50)
    voucher_for_item.save()

    resp = token_client.get(
        f"/api/v1/organizers/dummy/events/dummy/extended-vouchers/{voucher_for_item.code}/",
        format="json",
    )

    assert resp.status_code == 404


def test_used_voucher_is_not_returned(token_client, voucher_for_item):
    voucher_for_item.redeemed = 1
    voucher_for_item.max_usages = 1
    voucher_for_item.save()

    resp = token_client.get(
        f"/api/v1/organizers/dummy/events/dummy/extended-vouchers/{voucher_for_item.code}/",
        format="json",
    )

    assert resp.status_code == 404
