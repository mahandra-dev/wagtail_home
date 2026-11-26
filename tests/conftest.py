import pytest
from django.core.management import call_command
from wagtail.models import Page


@pytest.fixture
def root_page(db):
    return Page.get_first_root_node()


@pytest.fixture
def seeded(db):
    """The demo site from `seed_site`, returned as {slug: specific page}."""
    call_command("seed_site", verbosity=0)
    return {p.slug: p for p in Page.objects.filter(depth__gte=2).specific()}
