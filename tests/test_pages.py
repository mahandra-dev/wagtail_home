import pytest
from django.core.exceptions import ValidationError
from django.core.management import call_command
from wagtail.models import Page, Site

from home.models import ContactPage, HomePage, StandardPage
from navigation.models import Menu

pytestmark = pytest.mark.django_db


class TestParentChildRules:
    def test_home_page_only_at_root(self, seeded, root_page):
        home = seeded["home"]
        assert HomePage.allowed_parent_page_models() == [Page]
        assert not HomePage.can_create_at(home)

    def test_home_page_max_count(self, seeded, root_page):
        assert HomePage.objects.count() == 1
        assert not HomePage.can_create_at(root_page)

    def test_home_page_can_be_created_on_empty_root(self, root_page):
        for page in root_page.get_children():
            page.delete()
        assert HomePage.can_create_at(root_page)
        home = HomePage(title="Home", slug="home")
        root_page.add_child(instance=home)
        assert home.depth == 2

    def test_standard_page_under_home_and_standard(self, seeded, root_page):
        assert StandardPage.can_create_at(seeded["home"])
        assert StandardPage.can_create_at(seeded["about"])
        assert not StandardPage.can_create_at(root_page)
        assert not StandardPage.can_create_at(seeded["contact"])

    def test_contact_page_rules(self, seeded):
        # max_count = 1 and it already exists
        assert not ContactPage.can_create_at(seeded["home"])
        assert ContactPage.allowed_parent_page_models() == [HomePage]
        assert not StandardPage.can_create_at(seeded["contact"])
        assert ContactPage.allowed_subpage_models() == []

    def test_contact_page_not_under_standard_page(self, seeded):
        seeded["contact"].delete()
        assert ContactPage.can_create_at(seeded["home"])
        assert not ContactPage.can_create_at(seeded["about"])


class TestHomePageValidation:
    def test_cta_page_and_url_conflict(self, seeded):
        home = seeded["home"]
        home.hero_cta_url = "https://example.com"
        with pytest.raises(ValidationError):
            home.full_clean()

    def test_cta_text_without_link(self, seeded):
        home = seeded["home"]
        home.hero_cta_page = None
        home.hero_cta_url = ""
        with pytest.raises(ValidationError):
            home.full_clean()


class TestSeedAndRendering:
    def test_seed_creates_tree(self, seeded):
        assert set(seeded) >= {"home", "about", "services", "web-design", "consulting", "contact"}
        assert seeded["web-design"].get_parent().specific == seeded["services"]
        assert Site.objects.get(is_default_site=True).root_page_id == seeded["home"].pk
        assert set(Menu.objects.values_list("slug", flat=True)) == {"main", "footer"}

    def test_seed_is_idempotent(self, seeded):
        call_command("seed_site", verbosity=0)
        assert HomePage.objects.count() == 1
        assert StandardPage.objects.count() == 4
        assert Menu.objects.count() == 2

    def test_seed_force_recreates(self, seeded):
        call_command("seed_site", "--force", verbosity=0)
        assert HomePage.objects.count() == 1
        assert Menu.objects.count() == 2

    @pytest.mark.parametrize(
        "path", ["/", "/about/", "/services/", "/services/web-design/", "/contact/"]
    )
    def test_pages_render(self, client, seeded, path):
        response = client.get(path)
        assert response.status_code == 200
        assert b'<nav id="main-nav"' in response.content

    def test_seo_fields_rendered(self, client, seeded):
        content = client.get("/").content.decode()
        assert "<title>Wagtail Home — a demo site" in content
        assert '<meta name="description" content="A demo Wagtail 7.4 site' in content

    def test_stream_blocks_rendered(self, client, seeded):
        content = client.get("/about/").content.decode()
        assert '<h2 class="block-heading">Our story</h2>' in content
        assert '<figure class="block-quote">' in content
