import pytest
from rest_framework.test import APIClient
from django_scopes import scopes_disabled
from pretix.base.models import Event, Organizer, Team
from datetime import datetime
from pytz import UTC


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
    return Organizer.objects.create(name='Dummy', slug='dummy')


@pytest.fixture
@scopes_disabled()
def event(organizer, meta_prop):
    e = Event.objects.create(
        organizer=organizer, name='Dummy', slug='dummy',
        date_from=datetime(2017, 12, 27, 10, 0, 0, tzinfo=UTC),
        plugins='pretix_extended_api',
        is_public=True
    )
    e.meta_values.create(property=meta_prop, value="Conference")
    e.item_meta_properties.create(name="day", default="Monday")
    e.settings.timezone = 'Europe/Berlin'
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
        can_change_organizer_settings=True
    )



@pytest.fixture
@scopes_disabled()
def token_client(client, team):
    team.can_view_orders = True
    team.can_view_vouchers = True
    team.all_events = True
    team.save()
    t = team.tokens.create(name='Foo')
    client.credentials(HTTP_AUTHORIZATION='Token ' + t.token)
    return client
