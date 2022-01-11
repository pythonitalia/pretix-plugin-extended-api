import datetime
import pytest
from decimal import Decimal
from django_countries.fields import Country
from django_scopes import scopes_disabled
from pretix.base.models import (
    Event,
    InvoiceAddress,
    Order,
    OrderPosition,
    Organizer,
    Team,
    User,
)
from pytz import UTC
from rest_framework.test import APIClient
from unittest import mock


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
@scopes_disabled()
def meta_prop(organizer):
    return organizer.meta_properties.create(name="type", default="Concert")


@pytest.fixture
@scopes_disabled()
def organizer():
    return Organizer.objects.create(name="Dummy", slug="dummy")


@pytest.fixture
@scopes_disabled()
def organizer2():
    return Organizer.objects.create(name="Python Italia", slug="python-italia")


@pytest.fixture
@scopes_disabled()
def event(organizer, meta_prop):
    e = Event.objects.create(
        organizer=organizer,
        name="Dummy",
        slug="dummy",
        date_from=datetime.datetime(2017, 12, 27, 10, 0, 0, tzinfo=UTC),
        plugins="pretix_extended_api",
        is_public=True,
    )
    e.meta_values.create(property=meta_prop, value="Conference")
    e.item_meta_properties.create(name="day", default="Monday")
    e.settings.timezone = "Europe/Berlin"
    return e


@pytest.fixture
@scopes_disabled()
def event2(organizer2, meta_prop):
    e = Event.objects.create(
        organizer=organizer2,
        name="Smart",
        slug="smart",
        date_from=datetime.datetime(2017, 12, 27, 10, 0, 0, tzinfo=UTC),
        plugins="pretix_extended_api",
        is_public=True,
    )
    e.meta_values.create(property=meta_prop, value="Conference")
    e.item_meta_properties.create(name="day", default="Monday")
    e.settings.timezone = "Europe/Berlin"
    return e


@pytest.fixture
@scopes_disabled()
def team(organizer):
    return Team.objects.create(
        organizer=organizer,
        name="Test-Team",
        can_change_teams=True,
        can_manage_gift_cards=True,
        can_change_items=True,
        can_create_events=True,
        can_change_event_settings=True,
        can_change_vouchers=True,
        can_view_vouchers=True,
        can_change_orders=True,
        can_manage_customers=True,
        can_change_organizer_settings=True,
    )


@pytest.fixture
@scopes_disabled()
def token_client(client, team):
    team.can_view_orders = True
    team.can_view_vouchers = True
    team.all_events = True
    team.save()
    t = team.tokens.create(name="Foo")
    client.credentials(HTTP_AUTHORIZATION="Token " + t.token)
    return client


@pytest.fixture
@scopes_disabled()
def no_permissions_token_client(client, team):
    team.can_view_orders = False
    team.can_view_vouchers = False
    team.all_events = False
    team.save()
    t = team.tokens.create(name="Foo")
    client.credentials(HTTP_AUTHORIZATION="Token " + t.token)
    return client


@pytest.fixture
@scopes_disabled()
def admission_item(event):
    return event.items.create(name="Budget Ticket", admission=True, default_price=23)


@pytest.fixture
@scopes_disabled()
def normal_item(event):
    return event.items.create(name="Another thing", admission=False, default_price=23)


@pytest.fixture
@scopes_disabled()
def admission_item_event2(event2):
    return event2.items.create(name="Budget Ticket", admission=True, default_price=23)


@pytest.fixture
@scopes_disabled()
def order(event, admission_item):
    testtime = datetime.datetime(2017, 12, 1, 10, 0, 0, tzinfo=UTC)
    event.plugins += ",pretix.plugins.stripe"
    event.save()

    with mock.patch("django.utils.timezone.now") as mock_now:
        mock_now.return_value = testtime
        o = Order.objects.create(
            code="FOO",
            event=event,
            email="dummy@dummy.test",
            status=Order.STATUS_PAID,
            secret="k24fiuwvu8kxz3y1",
            datetime=datetime.datetime(2017, 12, 1, 10, 0, 0, tzinfo=UTC),
            expires=datetime.datetime(2017, 12, 10, 10, 0, 0, tzinfo=UTC),
            total=23,
            locale="en",
        )
        o.payments.create(
            provider="banktransfer",
            state="pending",
            amount=Decimal("23.00"),
        )
        InvoiceAddress.objects.create(
            order=o,
            company="Sample company",
            country=Country("NZ"),
            vat_id="DE123",
            vat_id_validated=True,
        )
        OrderPosition.objects.create(
            order=o,
            item=admission_item,
            variation=None,
            price=Decimal("23"),
            attendee_name_parts={"full_name": "Peter", "_scheme": "full"},
            attendee_email="test@email.it",
            secret="z3fsn8jyufm5kpk768q69gkbyr5f4h6w",
            pseudonymization_id="ABCDEFGHKL",
        )
        return o


@pytest.fixture
@scopes_disabled()
def no_admission_order(event, normal_item):
    testtime = datetime.datetime(2017, 12, 1, 10, 0, 0, tzinfo=UTC)
    event.plugins += ",pretix.plugins.stripe"
    event.save()

    with mock.patch("django.utils.timezone.now") as mock_now:
        mock_now.return_value = testtime
        o = Order.objects.create(
            code="FOO",
            event=event,
            email="dummy@dummy.test",
            status=Order.STATUS_PAID,
            secret="k24fiuwvu8kxz3y1",
            datetime=datetime.datetime(2017, 12, 1, 10, 0, 0, tzinfo=UTC),
            expires=datetime.datetime(2017, 12, 10, 10, 0, 0, tzinfo=UTC),
            total=23,
            locale="en",
        )
        o.payments.create(
            provider="banktransfer",
            state="pending",
            amount=Decimal("23.00"),
        )
        InvoiceAddress.objects.create(
            order=o,
            company="Sample company",
            country=Country("NZ"),
            vat_id="DE123",
            vat_id_validated=True,
        )
        OrderPosition.objects.create(
            order=o,
            item=normal_item,
            variation=None,
            price=Decimal("23"),
            attendee_name_parts={"full_name": "Peter", "_scheme": "full"},
            attendee_email="test@email.it",
            secret="z3fsn8jyufm5kpk768q69gkbyr5f4h6w",
            pseudonymization_id="ABCDEFGHKL",
        )
        return o


@pytest.fixture
@scopes_disabled()
def order_event_2(event2, admission_item_event2):
    testtime = datetime.datetime(2017, 12, 1, 10, 0, 0, tzinfo=UTC)
    event2.plugins += ",pretix.plugins.stripe"
    event2.save()

    with mock.patch("django.utils.timezone.now") as mock_now:
        mock_now.return_value = testtime
        o = Order.objects.create(
            code="FOO",
            event=event2,
            email="dummy@dummy.test",
            status=Order.STATUS_PAID,
            secret="k24fiuwvu8kxz3y1",
            datetime=datetime.datetime(2017, 12, 1, 10, 0, 0, tzinfo=UTC),
            expires=datetime.datetime(2017, 12, 10, 10, 0, 0, tzinfo=UTC),
            total=23,
            locale="en",
        )
        o.payments.create(
            provider="banktransfer",
            state="pending",
            amount=Decimal("23.00"),
        )
        InvoiceAddress.objects.create(
            order=o,
            company="Sample company",
            country=Country("NZ"),
            vat_id="DE123",
            vat_id_validated=True,
        )
        OrderPosition.objects.create(
            order=o,
            item=admission_item_event2,
            variation=None,
            price=Decimal("23"),
            attendee_name_parts={"full_name": "Peter", "_scheme": "full"},
            attendee_email="test@email.it",
            secret="z3fsn8jyufm5kpk768q69gkbyr5f4h6w",
            pseudonymization_id="ABCDEFGHKL",
        )
        return o


@pytest.fixture
def user():
    return User.objects.create_user('dummy@dummy.dummy', 'dummy')


@pytest.fixture
@scopes_disabled()
def user_client(client, team, user):
    team.can_view_orders = True
    team.can_view_vouchers = True
    team.all_events = True
    team.save()
    team.members.add(user)
    client.force_authenticate(user=user)
    return client
