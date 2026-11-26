import pytest
from django.core.exceptions import ValidationError
from wagtail.blocks.struct_block import StructBlockValidationError

from core.blocks import CallToActionBlock
from navigation.models import Menu, MenuItem, SubMenuItem

pytestmark = pytest.mark.django_db


@pytest.fixture
def menu(db):
    return Menu.objects.create(title="Test", slug="test")


class TestMenuItemValidation:
    def test_page_and_url_both_set_is_invalid(self, menu, seeded):
        item = MenuItem(
            menu=menu, link_page=seeded["about"], link_url="https://example.com", link_title="X"
        )
        with pytest.raises(ValidationError) as exc:
            item.full_clean()
        assert "link_page" in exc.value.message_dict
        assert "link_url" in exc.value.message_dict

    def test_neither_page_nor_url_is_invalid(self, menu):
        item = MenuItem(menu=menu, link_title="Nowhere")
        with pytest.raises(ValidationError):
            item.full_clean()

    def test_external_url_requires_title(self, menu):
        item = MenuItem(menu=menu, link_url="https://example.com")
        with pytest.raises(ValidationError) as exc:
            item.full_clean()
        assert "link_title" in exc.value.message_dict

    def test_page_only_is_valid_and_title_falls_back(self, menu, seeded):
        item = MenuItem(menu=menu, link_page=seeded["about"])
        item.full_clean()
        assert item.title == "About"
        assert item.url == "/about/"

    def test_explicit_title_wins(self, menu, seeded):
        item = MenuItem(menu=menu, link_page=seeded["about"], link_title="Who we are")
        assert item.title == "Who we are"

    def test_url_only_is_valid(self, menu):
        item = MenuItem(menu=menu, link_url="https://example.com", link_title="Example")
        item.full_clean()
        assert item.url == "https://example.com"

    def test_sub_item_uses_same_validation(self, menu, seeded):
        parent = MenuItem.objects.create(menu=menu, link_page=seeded["services"])
        sub = SubMenuItem(parent=parent)
        with pytest.raises(ValidationError):
            sub.full_clean()


class TestCallToActionBlock:
    def test_requires_exactly_one_target(self, seeded):
        block = CallToActionBlock()
        with pytest.raises(StructBlockValidationError):
            block.clean(block.to_python({"text": "Go", "page": None, "url": ""}))
        with pytest.raises(StructBlockValidationError):
            block.clean(
                block.to_python(
                    {"text": "Go", "page": seeded["about"].pk, "url": "https://example.com"}
                )
            )
        block.clean(block.to_python({"text": "Go", "page": None, "url": "https://example.com"}))
