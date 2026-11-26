"""Admin-editable menus.

Structure (one level of nesting, enforced by the schema itself):

    Menu (snippet)
     └── MenuItem   (Orderable inline on Menu)
          └── SubMenuItem (Orderable inline nested inside MenuItem)

Nested InlinePanels are natively supported by Wagtail/modelcluster, so editors
manage dropdown children directly inside their parent item, and a deeper level
or a cycle simply cannot be expressed.
"""

from django.core.exceptions import ValidationError
from django.db import models
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel
from wagtail.models import Orderable
from wagtail.search import index
from wagtail.snippets.models import register_snippet


class LinkFields(models.Model):
    """A link to either an internal page or an external URL (exactly one)."""

    link_title = models.CharField(
        max_length=255,
        blank=True,
        help_text="Leave empty to use the linked page's title.",
    )
    link_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="+",
    )
    link_url = models.URLField("External URL", blank=True)
    open_in_new_tab = models.BooleanField(default=False)

    link_panels = [
        FieldPanel("link_title"),
        FieldRowPanel([FieldPanel("link_page"), FieldPanel("link_url")]),
        FieldPanel("open_in_new_tab"),
    ]

    class Meta:
        abstract = True

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        has_page = self.link_page_id is not None
        has_url = bool(self.link_url)
        if has_page and has_url:
            msg = "Choose either a page or an external URL, not both."
            raise ValidationError({"link_page": msg, "link_url": msg})
        if not has_page and not has_url:
            msg = "Choose a page or enter an external URL."
            raise ValidationError({"link_page": msg, "link_url": msg})
        if has_url and not self.link_title:
            raise ValidationError({"link_title": "A title is required for external links."})

    @property
    def title(self):
        if self.link_title:
            return self.link_title
        if self.link_page_id:
            return self.link_page.title
        return self.link_url

    def get_url(self, request=None):
        if self.link_page_id:
            return self.link_page.get_url(request=request)
        return self.link_url

    @property
    def url(self):
        return self.get_url()

    def is_visible(self):
        """External links are always shown; page links only if live and in menus."""
        if not self.link_page_id:
            return True
        return self.link_page.live and self.link_page.show_in_menus


@register_snippet
class Menu(index.Indexed, ClusterableModel):
    title = models.CharField(max_length=100)
    slug = models.SlugField(
        max_length=100,
        unique=True,
        help_text='Used in templates, e.g. {% menu "main" %}.',
    )

    panels = [
        MultiFieldPanel([FieldPanel("title"), FieldPanel("slug")], heading="Menu"),
        InlinePanel("menu_items", label="Menu items"),
    ]

    search_fields = [index.SearchField("title"), index.AutocompleteField("title")]

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class MenuItem(LinkFields, ClusterableModel, Orderable):
    menu = ParentalKey(Menu, on_delete=models.CASCADE, related_name="menu_items")

    panels = LinkFields.link_panels + [
        InlinePanel("sub_items", label="Dropdown items"),
    ]

    class Meta(Orderable.Meta):
        verbose_name = "menu item"


class SubMenuItem(LinkFields, Orderable):
    parent = ParentalKey(MenuItem, on_delete=models.CASCADE, related_name="sub_items")

    panels = LinkFields.link_panels

    class Meta(Orderable.Meta):
        verbose_name = "dropdown item"
