# Module Catalog

All major modules, their public APIs and key structures (from AST scan + source review).
Full signatures: [signatures.md](./signatures.md).

## Module: config (`config/`)

### Overview
Django project package. No business logic.

| File | Purpose |
| :--- | :--- |
| `config/settings/base.py` | All shared settings; every environment-specific value comes from `environ.Env` (reads `.env` if present, real env wins). Defines `INSTALLED_APPS`, Postgres via `DATABASE_URL`, email via `EMAIL_URL`, Wagtail search (database backend), docs upload limits, logging. |
| `config/settings/dev.py` | `from .base import *`; `DEBUG` default True, `ALLOWED_HOSTS` default `*`. Used by `manage.py` and pytest. |
| `config/settings/prod.py` | `DEBUG=False`, WhiteNoise middleware + `CompressedManifestStaticFilesStorage`, SSL redirect, HSTS, secure cookies, `X_FRAME_OPTIONS=DENY`. |
| `config/urls.py` | `django-admin/`, `admin/` (Wagtail), `documents/`, static/media in DEBUG, then Wagtail catch-all (must stay last). |
| `config/wsgi.py`, `config/asgi.py` | Standard Django application objects. |

## Module: home (`home/`)

### Overview
Page types and demo-content seeding.

### Exported Classes
| Symbol | Kind | Lines | Description |
| :--- | :--- | :--- | :--- |
| `HomePage` | `Page` | L19-L82 | Site root. `max_count=1`, parent `wagtailcore.Page`, children `StandardPage`/`ContactPage`. Hero fields (`hero_title`, `hero_subtitle`, `hero_image`, `hero_cta_text`, `hero_cta_page`, `hero_cta_url`) + `body` StreamField. |
| `StandardPage` | `Page` | L85-L105 | Generic page; `intro` rich text + `body`. Parents: HomePage, StandardPage; children: StandardPage. |
| `FormField` | `AbstractFormField` | L108-L109 | Form field rows, `ParentalKey` to `ContactPage` (`related_name="form_fields"`). |
| `ContactPage` | `AbstractEmailForm` | L112-L143 | `max_count=1`, parent HomePage, no children. `intro`, `thank_you_text`, email settings (`from_address`, `to_address`, `subject`), `FormSubmissionsPanel`. |

### Public Functions & Methods
- `HomePage.hero_cta_href` (property) → URL of `hero_cta_page`, else `hero_cta_url`, else `""`.
- `HomePage.clean()` → rejects page **and** URL together; rejects `hero_cta_text` without a target.

### Management command: `home/management/commands/seed_site.py`
- `Command.handle(*args, force=False, **options)` — `@transaction.atomic`; idempotent unless `--force`.
- Helpers: `_delete_existing`, `_delete_default_welcome_page(root)`, `_add(parent, page)` (add + publish revision), `_create_pages(root)`, `_configure_site(home)`, `_create_menus()`.
- Module-level StreamField builders: `heading(text, size="h2")`, `paragraph(html)`, `quote(text, attribution="")`, `cta(text, page=None, url="")` — return raw `{"type", "value"}` dicts.

### Internal References
- Imports: `core.blocks` (via models), `navigation.models` (seed).
- Dependent files: `tests/test_pages.py`, `tests/conftest.py` (calls `seed_site`).

## Module: navigation (`navigation/`)

### Overview
Admin-editable menus as Wagtail snippets. Hub module (imported by 5 files). Nesting is one
level by schema: nested `InlinePanel` (`SubMenuItem` inside `MenuItem`) instead of a
self-referencing FK, so deeper levels or cycles are impossible.

### Exported Classes
| Symbol | Kind | Description |
| :--- | :--- | :--- |
| `LinkFields` | abstract `models.Model` | `link_title`, `link_page` (FK Page, CASCADE), `link_url`, `open_in_new_tab`, shared `link_panels`. |
| `Menu` | `@register_snippet`, `index.Indexed`, `ClusterableModel` | `title`, unique `slug` (used by `{% menu "slug" %}`); inline `menu_items`. Ordered by title. |
| `MenuItem` | `LinkFields`, `ClusterableModel`, `Orderable` | `ParentalKey` → `Menu` (`menu_items`); inline `sub_items`. |
| `SubMenuItem` | `LinkFields`, `Orderable` | `ParentalKey` → `MenuItem` (`sub_items`). |

### Public Functions & Methods (`LinkFields`)
- `clean()` — exactly one of `link_page` / `link_url`; external URLs require `link_title`.
- `title` (property) — `link_title` → page title → URL.
- `get_url(request=None)` — page URL (site-relative) or `link_url`; `url` property = `get_url()`.
- `is_visible()` — external links always; page links only if `live and show_in_menus`.

### Internal References
- Dependent files: `core/templatetags/navigation_tags.py`, `home/management/commands/seed_site.py`, `tests/test_menu_validation.py`, `tests/test_navigation.py`, `tests/test_pages.py`.

## Module: core (`core/`)

### Overview
Shared presentation building blocks; no models.

### `core/blocks.py`
| Symbol | Base | Template | Notes |
| :--- | :--- | :--- | :--- |
| `HeadingBlock` | `StructBlock` | `blocks/heading.html` | `text`, `size` (h2/h3/h4). |
| `ParagraphBlock` | `RichTextBlock` | `blocks/paragraph.html` | Limited rich-text features. |
| `ImageWithCaptionBlock` | `StructBlock` | `blocks/image.html` | `image`, `alt_text` (falls back to image title), `caption`. |
| `QuoteBlock` | `StructBlock` | `blocks/quote.html` | `quote`, `attribution`. |
| `CallToActionBlock` | `StructBlock` | `blocks/cta.html` | `text`, `page` or `url`; `clean(value)` raises `StructBlockValidationError` unless exactly one is set. |
| `RawEmbedBlock` | `RawHTMLBlock` | `blocks/embed.html` | Unescaped HTML — trusted editors only. |
| `BaseStreamBlock` | `StreamBlock` | — | `heading`, `paragraph`, `image`, `quote`, `cta`, `embed`. Used by `HomePage.body` and `StandardPage.body`. |

### `core/templatetags/navigation_tags.py` (`{% load navigation_tags %}`)
- `NavLink` (dataclass): `title`, `url`, `open_in_new_tab`, `is_current`, `is_ancestor`, `children`; properties `is_active`, `aria_current` (`"page"` / `"true"` / `None`).
- `_build_link(item, current_page, request) -> NavLink` — active-state rules (site roots depth ≤ 2 only match exactly).
- `get_menu_links(slug, current_page=None, request=None) -> list[NavLink]` — prefetching query, visibility filter, parent marked ancestor when a child is active; `[]` for unknown slug.
- `menu(context, slug, template="navigation/menu.html")` — simple tag; takes `page` and `request` from context and renders the template with `menu_slug`, `links`, `request`.

## Templates & Static (`templates/`, `static/`)
| Path | Purpose |
| :--- | :--- |
| `templates/base.html` | Layout, SEO `<title>`/description/canonical, skip link, header + main menu + mobile toggle, footer menu, `wagtailuserbar`. |
| `templates/home/home_page.html`, `standard_page.html`, `contact_page.html`, `contact_page_landing.html` | One template per page type (+ form landing). |
| `templates/blocks/*.html` | One template per StreamField block. |
| `templates/navigation/menu.html`, `footer_menu.html` | Menu markup (`aria-current`, `is-active`, `submenu`, `target="_blank" rel="noopener noreferrer"`). |
| `templates/404.html`, `500.html` | Error pages. |
| `static/js/nav.js` | Dependency-free mobile toggle, dropdown toggles, Escape-to-close. |
| `static/css/site.css` | Site stylesheet. |

## Tests (`tests/`)
| File | Covers |
| :--- | :--- |
| `tests/conftest.py` | Fixtures `root_page`, `seeded` (runs `seed_site`, returns `{slug: specific page}`). |
| `tests/test_pages.py` | Parent/child rules, `max_count`, HomePage CTA validation, seeding (idempotent / `--force`), page rendering, SEO fields, StreamField blocks. |
| `tests/test_menu_validation.py` | `LinkFields.clean`, title/URL fallbacks, `CallToActionBlock.clean`. |
| `tests/test_navigation.py` | Menu rendering, dropdown, footer, landmarks, active state, visibility (`show_in_menus`, unpublished), missing menu, admin edit view with nested inline. |
| `tests/test_contact_form.py` | Form render, valid submission (stored + emailed), invalid submission. |
