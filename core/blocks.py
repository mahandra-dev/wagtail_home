"""Shared StreamField blocks used by all page types."""

from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList
from wagtail import blocks
from wagtail.blocks.struct_block import StructBlockValidationError
from wagtail.images.blocks import ImageChooserBlock


class HeadingBlock(blocks.StructBlock):
    text = blocks.CharBlock(max_length=255)
    size = blocks.ChoiceBlock(
        choices=[("h2", "H2"), ("h3", "H3"), ("h4", "H4")],
        default="h2",
    )

    class Meta:
        icon = "title"
        template = "blocks/heading.html"


class ParagraphBlock(blocks.RichTextBlock):
    class Meta:
        icon = "pilcrow"
        template = "blocks/paragraph.html"
        features = ["h2", "h3", "bold", "italic", "link", "ol", "ul", "hr", "document-link"]


class ImageWithCaptionBlock(blocks.StructBlock):
    image = ImageChooserBlock()
    alt_text = blocks.CharBlock(
        required=False,
        max_length=255,
        help_text="Describe the image for screen readers. Leave empty to use the image title.",
    )
    caption = blocks.CharBlock(required=False, max_length=255)

    class Meta:
        icon = "image"
        template = "blocks/image.html"


class QuoteBlock(blocks.StructBlock):
    quote = blocks.TextBlock()
    attribution = blocks.CharBlock(required=False, max_length=255)

    class Meta:
        icon = "openquote"
        template = "blocks/quote.html"


class CallToActionBlock(blocks.StructBlock):
    """A button-style link to an internal page OR an external URL (exactly one)."""

    text = blocks.CharBlock(max_length=100)
    page = blocks.PageChooserBlock(required=False)
    url = blocks.URLBlock(required=False, label="External URL")

    class Meta:
        icon = "link"
        template = "blocks/cta.html"

    def clean(self, value):
        value = super().clean(value)
        has_page = bool(value.get("page"))
        has_url = bool(value.get("url"))
        if has_page == has_url:
            msg = "Choose either an internal page or an external URL (exactly one)."
            raise StructBlockValidationError(
                block_errors={
                    "page": ErrorList([ValidationError(msg)]),
                    "url": ErrorList([ValidationError(msg)]),
                }
            )
        return value


class RawEmbedBlock(blocks.RawHTMLBlock):
    """Raw HTML embed (iframes, widgets). Editors must be trusted."""

    class Meta:
        icon = "code"
        label = "Raw embed (HTML)"
        template = "blocks/embed.html"


class BaseStreamBlock(blocks.StreamBlock):
    heading = HeadingBlock()
    paragraph = ParagraphBlock()
    image = ImageWithCaptionBlock()
    quote = QuoteBlock()
    cta = CallToActionBlock(label="Call to action")
    embed = RawEmbedBlock()
