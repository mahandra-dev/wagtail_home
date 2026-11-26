from django.core.exceptions import ValidationError
from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    InlinePanel,
    MultiFieldPanel,
)
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.contrib.forms.panels import FormSubmissionsPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page
from wagtail.search import index

from core.blocks import BaseStreamBlock


class HomePage(Page):
    """Site root. Exactly one may exist, directly under the tree root."""

    hero_title = models.CharField(max_length=255, blank=True)
    hero_subtitle = models.TextField(blank=True)
    hero_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    hero_cta_text = models.CharField("CTA text", max_length=100, blank=True)
    hero_cta_page = models.ForeignKey(
        "wagtailcore.Page",
        verbose_name="CTA page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    hero_cta_url = models.URLField("CTA external URL", blank=True)
    body = StreamField(BaseStreamBlock(), blank=True, use_json_field=True)

    max_count = 1
    parent_page_types = ["wagtailcore.Page"]
    subpage_types = ["home.StandardPage", "home.ContactPage"]

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("hero_title"),
                FieldPanel("hero_subtitle"),
                FieldPanel("hero_image"),
                FieldPanel("hero_cta_text"),
                FieldRowPanel([FieldPanel("hero_cta_page"), FieldPanel("hero_cta_url")]),
            ],
            heading="Hero",
        ),
        FieldPanel("body"),
    ]

    search_fields = Page.search_fields + [
        index.SearchField("hero_title"),
        index.SearchField("hero_subtitle"),
        index.SearchField("body"),
    ]

    class Meta:
        verbose_name = "Home page"

    @property
    def hero_cta_href(self):
        if self.hero_cta_page_id:
            return self.hero_cta_page.url
        return self.hero_cta_url or ""

    def clean(self):
        super().clean()
        if self.hero_cta_page_id and self.hero_cta_url:
            msg = "Choose either a CTA page or a CTA external URL, not both."
            raise ValidationError({"hero_cta_page": msg, "hero_cta_url": msg})
        if self.hero_cta_text and not (self.hero_cta_page_id or self.hero_cta_url):
            raise ValidationError({"hero_cta_text": "A CTA needs a page or an external URL."})


class StandardPage(Page):
    """Generic content page: About, Services, etc."""

    intro = RichTextField(blank=True, features=["bold", "italic", "link"])
    body = StreamField(BaseStreamBlock(), blank=True, use_json_field=True)

    parent_page_types = ["home.HomePage", "home.StandardPage"]
    subpage_types = ["home.StandardPage"]

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("body"),
    ]

    search_fields = Page.search_fields + [
        index.SearchField("intro"),
        index.SearchField("body"),
    ]

    class Meta:
        verbose_name = "Standard page"


class FormField(AbstractFormField):
    page = ParentalKey("ContactPage", on_delete=models.CASCADE, related_name="form_fields")


class ContactPage(AbstractEmailForm):
    """Contact form; submissions are stored and optionally emailed to `to_address`."""

    intro = RichTextField(blank=True, features=["bold", "italic", "link"])
    thank_you_text = RichTextField(
        blank=True,
        features=["bold", "italic", "link"],
        help_text="Landing text shown after a successful submission.",
    )

    max_count = 1
    parent_page_types = ["home.HomePage"]
    subpage_types = []

    content_panels = AbstractEmailForm.content_panels + [
        FormSubmissionsPanel(),
        FieldPanel("intro"),
        InlinePanel("form_fields", label="Form fields"),
        FieldPanel("thank_you_text"),
        MultiFieldPanel(
            [
                FieldRowPanel([FieldPanel("from_address"), FieldPanel("to_address")]),
                FieldPanel("subject"),
            ],
            heading="Email settings",
        ),
    ]

    search_fields = Page.search_fields + [index.SearchField("intro")]

    class Meta:
        verbose_name = "Contact page"
