import re

import pytest
from django.contrib.auth import get_user_model
from django.template import Context, Template
from django.test import RequestFactory

from navigation.models import Menu

pytestmark = pytest.mark.django_db


def main_nav(html):
    return re.search(r'<nav id="main-nav".*?</nav>', html, re.S).group(0)


def link(html, href):
    """Return the <a ...> tag pointing at href."""
    match = re.search(rf'<a [^>]*href="{re.escape(href)}"[^>]*>', html)
    assert match, f"no link to {href}"
    return match.group(0)


class TestMenuRendering:
    def test_main_menu_items_and_dropdown(self, client, seeded):
        nav = main_nav(client.get("/about/").content.decode())
        for href in ["/", "/about/", "/services/", "/contact/"]:
            assert f'href="{href}"' in nav
        assert 'class="submenu"' in nav
        assert 'href="/services/web-design/"' in nav
        assert 'href="/services/consulting/"' in nav
        assert ">Web Design</a>" in nav  # empty link_title falls back to page title

    def test_footer_menu(self, client, seeded):
        html = client.get("/").content.decode()
        footer = re.search(r'<nav class="footer-nav".*?</nav>', html, re.S).group(0)
        assert ">About us</a>" in footer
        assert 'href="https://wagtail.org/" target="_blank" rel="noopener noreferrer"' in footer

    def test_nav_landmarks(self, client, seeded):
        html = client.get("/").content.decode()
        assert 'aria-label="Main"' in html
        assert 'aria-label="Footer"' in html

    def test_missing_menu_renders_nothing(self, seeded):
        rendered = Template('{% load navigation_tags %}{% menu "nope" %}').render(
            Context({"request": RequestFactory().get("/")})
        )
        assert rendered.strip() == ""


class TestActiveState:
    def test_current_page_marked(self, client, seeded):
        nav = main_nav(client.get("/about/").content.decode())
        assert 'aria-current="page"' in link(nav, "/about/")
        assert "aria-current" not in link(nav, "/services/")

    def test_home_not_active_on_subpages(self, client, seeded):
        nav = main_nav(client.get("/about/").content.decode())
        assert "aria-current" not in link(nav, "/")

    def test_home_active_on_home(self, client, seeded):
        nav = main_nav(client.get("/").content.decode())
        assert 'aria-current="page"' in link(nav, "/")
        assert nav.count('aria-current="page"') == 1

    def test_ancestor_highlighted_for_child_page(self, client, seeded):
        nav = main_nav(client.get("/services/web-design/").content.decode())
        assert 'aria-current="page"' in link(nav, "/services/web-design/")
        assert 'aria-current="true"' in link(nav, "/services/")
        assert "aria-current" not in link(nav, "/services/consulting/")
        assert re.search(r'class="menu__item menu__item--has-children is-active"', nav)

    def test_page_below_menu_item_highlights_ancestor(self, client, seeded):
        """A page not in the menu still highlights its nearest menu ancestor."""
        from home.models import StandardPage

        deep = StandardPage(title="Team", slug="team")
        seeded["about"].add_child(instance=deep)
        nav = main_nav(client.get("/about/team/").content.decode())
        assert 'aria-current="true"' in link(nav, "/about/")


class TestVisibility:
    def test_show_in_menus_false_hides_item(self, client, seeded):
        about = seeded["about"]
        about.show_in_menus = False
        about.save_revision().publish()
        nav = main_nav(client.get("/").content.decode())
        assert 'href="/about/"' not in nav

    def test_unpublished_page_hidden(self, client, seeded):
        seeded["consulting"].unpublish()
        nav = main_nav(client.get("/").content.decode())
        assert 'href="/services/consulting/"' not in nav


class TestAdmin:
    def test_menu_snippet_edit_view_with_nested_inline(self, client, seeded):
        user = get_user_model().objects.create_superuser("admin", "a@example.com", "pw")
        client.force_login(user)
        menu = Menu.objects.get(slug="main")
        response = client.get(f"/admin/snippets/navigation/menu/edit/{menu.pk}/")
        assert response.status_code == 200
        content = response.content.decode()
        assert "menu_items" in content
        assert "sub_items" in content
