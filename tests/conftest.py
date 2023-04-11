import datetime
import pytest
from decimal import Decimal
from django_countries.fields import Country
from django_scopes import scopes_disabled
from i18nfield.strings import LazyI18nString
from pretix.base.models import (
    Event,
    InvoiceAddress,
    Order,
    OrderPosition,
    Organizer,
    Question,
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
        name=LazyI18nString({"en": "Dummy", "it": "Prova"}),
        slug="dummy",
        date_from=datetime.datetime(2017, 12, 27, 10, 0, 0, tzinfo=UTC),
        plugins="pretix_extended_api",
        is_public=True,
    )
    e.meta_values.create(property=meta_prop, value="Conference")
    e.item_meta_properties.create(name="day", default="Monday")
    e.settings.timezone = "Europe/Berlin"
    e.settings.locales = ["en", "it"]

    return e


@pytest.fixture
@scopes_disabled()
def event_question(event):
    q = Question.objects.create(
        question=LazyI18nString({"en": "Tagline", "it": "Descrizione"}),
        type=Question.TYPE_TEXT,
        event=event,
    )
    q1 = Question.objects.create(
        event=event,
        question=LazyI18nString(
            {"en": "What do you want to eat?", "it": "'Sa magnet?!?! "}
        ),
        type=Question.TYPE_CHOICE,
        required=True,
    )
    q1.options.create(answer="Sushi", identifier="Sushi")
    q1.options.create(answer="Fiorentina", identifier="Fiorentina")
    return event, [q, q1]


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
    return event.items.create(
        name=LazyI18nString({"en": "Budget Ticket", "it": "Biglietto Economico"}),
        admission=True,
        default_price=23,
    )


@pytest.fixture
@scopes_disabled()
def normal_item(event):
    return event.items.create(name="Another thing", admission=False, default_price=23)


@pytest.fixture
@scopes_disabled()
def admission_item_event2(event2):
    return event2.items.create(
        name=LazyI18nString({"en": "Pricy Ticket", "it": "Biglietto Costoso"}),
        admission=True,
        default_price=23,
    )


@pytest.fixture
@scopes_disabled()
def order(event_question, admission_item):
    event, questions = event_question
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
        op = OrderPosition.objects.create(
            order=o,
            item=admission_item,
            variation=None,
            price=Decimal("23"),
            attendee_name_parts={"full_name": "Peter", "_scheme": "full"},
            attendee_email="test@email.it",
            secret="z3fsn8jyufm5kpk768q69gkbyr5f4h6w",
            pseudonymization_id="ABCDEFGHKL",
        )
        op.answers.create(question=questions[0], answer="PySushi")
        op.answers.create(question=questions[1], answer="Fiorentina")
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
            attendee_email="",
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
            price=Decimal("54"),
            attendee_name_parts={"full_name": "Peter", "_scheme": "full"},
            attendee_email="test@email.it",
            secret="z3fsn8jyufm5kpk768q69gkbyr5f4h6w",
            pseudonymization_id="MNOPQRSTUV",
        )
        return o


@pytest.fixture
def user():
    return User.objects.create_user("dummy@dummy.dummy", "dummy")


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


@pytest.fixture
@scopes_disabled()
def voucher_for_item(event, admission_item):
    return event.vouchers.create(
        item=admission_item, price_mode="set", value=12, tag="Foo"
    )


@pytest.fixture
@scopes_disabled()
def voucher_for_quota(event, quota):
    return event.vouchers.create(
        item=None, quota=quota, price_mode="set", value=12, tag="Foo"
    )


@pytest.fixture
@scopes_disabled()
def voucher_for_all_items(event):
    return event.vouchers.create(
        item=None, quota=None, price_mode="set", value=12, tag="Foo"
    )


@pytest.fixture
@scopes_disabled()
def quota(event, admission_item):
    q = event.quotas.create(name="Budget Quota", size=200)
    q.items.add(admission_item)
    return q
