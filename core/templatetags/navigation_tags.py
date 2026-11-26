"""Menu rendering.

{% menu "main" %}
{% menu "footer" template="navigation/footer_menu.html" %}
"""

from dataclasses import dataclass, field

from django import template
from django.template.loader import render_to_string
from wagtail.models import Page

from navigation.models import Menu

register = template.Library()

DEFAULT_TEMPLATE = "navigation/menu.html"


@dataclass
class NavLink:
    title: str
    url: str
    open_in_new_tab: bool = False
    is_current: bool = False  # this exact page is being viewed
    is_ancestor: bool = False  # the viewed page lives below this one
    children: list["NavLink"] = field(default_factory=list)

    @property
    def is_active(self):
        return self.is_current or self.is_ancestor

    @property
    def aria_current(self):
        """'page' for the current page, 'true' for the active section, else None."""
        if self.is_current:
            return "page"
        if self.is_ancestor:
            return "true"
        return None


def _build_link(item, current_page, request):
    link = NavLink(
        title=item.title,
        url=item.get_url(request),
        open_in_new_tab=item.open_in_new_tab,
    )
    target = item.link_page
    if target is not None and current_page is not None:
        if target.pk == current_page.pk:
            link.is_current = True
        # Site roots (depth <= 2) would be an "ancestor" of every page, so they
        # are only highlighted on an exact match.
        elif target.depth > 2 and current_page.path.startswith(target.path):
            link.is_ancestor = True
    return link


def get_menu_links(slug, current_page=None, request=None):
    menu = (
        Menu.objects.filter(slug=slug)
        .prefetch_related("menu_items__link_page", "menu_items__sub_items__link_page")
        .first()
    )
    if menu is None:
        return []

    links = []
    for item in menu.menu_items.all():
        if not item.is_visible():
            continue
        link = _build_link(item, current_page, request)
        for sub in item.sub_items.all():
            if sub.is_visible():
                link.children.append(_build_link(sub, current_page, request))
        if not link.is_current and any(child.is_active for child in link.children):
            link.is_ancestor = True
        links.append(link)
    return links


@register.simple_tag(takes_context=True)
def menu(context, slug, template=DEFAULT_TEMPLATE):
    request = context.get("request")
    current_page = context.get("page")
    if not isinstance(current_page, Page):
        current_page = None
    links = get_menu_links(slug, current_page=current_page, request=request)
    return render_to_string(
        template,
        {"menu_slug": slug, "links": links, "request": request},
    )
