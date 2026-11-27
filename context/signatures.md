# Codebase Signatures & Symbol Index

Quick-reference catalog of function and method signatures, arguments, and return types.

## [`config/settings/base.py`](../config/settings/base.py)

### Types & Interfaces
- `type_alias BASE_DIR` (L11)
- `type_alias SECRET_KEY` (L22)
- `type_alias DEBUG` (L23)
- `type_alias ALLOWED_HOSTS` (L24)
- `type_alias CSRF_TRUSTED_ORIGINS` (L25)
- `type_alias INSTALLED_APPS` (L27)
- `type_alias MIDDLEWARE` (L56)
- `type_alias ROOT_URLCONF` (L67)
- `type_alias TEMPLATES` (L69)
- `type_alias WSGI_APPLICATION` (L85)
- `type_alias DATABASES` (L88)
- `type_alias DEFAULT_AUTO_FIELD` (L92)
- `type_alias AUTH_PASSWORD_VALIDATORS` (L94)
- `type_alias LANGUAGE_CODE` (L101)
- `type_alias TIME_ZONE` (L102)
- `type_alias USE_I18N` (L103)
- `type_alias USE_TZ` (L104)
- `type_alias STATICFILES_FINDERS` (L107)
- `type_alias STATICFILES_DIRS` (L111)
- `type_alias STATIC_ROOT` (L112)
- `type_alias STATIC_URL` (L113)
- `type_alias MEDIA_ROOT` (L114)
- `type_alias MEDIA_URL` (L115)
- `type_alias STORAGES` (L117)
- `type_alias DATA_UPLOAD_MAX_NUMBER_FIELDS` (L123)
- `type_alias EMAIL_BACKEND` (L128)
- `type_alias EMAIL_HOST` (L129)
- `type_alias EMAIL_PORT` (L130)
- `type_alias EMAIL_HOST_USER` (L131)
- `type_alias EMAIL_HOST_PASSWORD` (L132)
- `type_alias EMAIL_USE_TLS` (L133)
- `type_alias EMAIL_USE_SSL` (L134)
- `type_alias DEFAULT_FROM_EMAIL` (L135)
- `type_alias SERVER_EMAIL` (L136)
- `type_alias WAGTAIL_SITE_NAME` (L139)
- `type_alias WAGTAILADMIN_BASE_URL` (L140)
- `type_alias WAGTAILSEARCH_BACKENDS` (L141)
- `type_alias WAGTAILDOCS_EXTENSIONS` (L144)
- `type_alias WAGTAILDOCS_MAX_UPLOAD_SIZE` (L145)
- `type_alias LOGGING` (L147)

## [`config/settings/dev.py`](../config/settings/dev.py)

### Types & Interfaces
- `type_alias DEBUG` (L6)
- `type_alias ALLOWED_HOSTS` (L7)

## [`config/settings/prod.py`](../config/settings/prod.py)

### Types & Interfaces
- `type_alias DEBUG` (L6)
- `type_alias MIDDLEWARE` (L9)
- `type_alias STORAGES` (L16)
- `type_alias SECURE_PROXY_SSL_HEADER` (L22)
- `type_alias SECURE_SSL_REDIRECT` (L23)
- `type_alias SECURE_HSTS_SECONDS` (L24)
- `type_alias SECURE_HSTS_INCLUDE_SUBDOMAINS` (L25)
- `type_alias SECURE_HSTS_PRELOAD` (L26)
- `type_alias SECURE_CONTENT_TYPE_NOSNIFF` (L27)
- `type_alias SECURE_REFERRER_POLICY` (L28)
- `type_alias SESSION_COOKIE_SECURE` (L29)
- `type_alias CSRF_COOKIE_SECURE` (L30)
- `type_alias X_FRAME_OPTIONS` (L31)

## [`core/apps.py`](../core/apps.py)

### Classes
- **`class CoreConfig`** (L4)

## [`core/blocks.py`](../core/blocks.py)

### Classes
- **`class HeadingBlock`** (L10)
- **`class ParagraphBlock`** (L22)
- **`class ImageWithCaptionBlock`** (L29)
- **`class QuoteBlock`** (L43)
- **`class CallToActionBlock`** (L52)
  *A button-style link to an internal page OR an external URL (exactly one).*
- **`class RawEmbedBlock`** (L78)
  *Raw HTML embed (iframes, widgets). Editors must be trusted.*
- **`class BaseStreamBlock`** (L87)

### Functions & Methods
| Symbol | Signature | Line | Callers |
| :--- | :--- | :--- | :--- |
| `CallToActionBlock.clean` | `clean(self, value)` | L63 | 3 |

## [`core/templatetags/navigation_tags.py`](../core/templatetags/navigation_tags.py)

### Classes
- **`class NavLink`** (L21)

### Functions & Methods
| Symbol | Signature | Line | Callers |
| :--- | :--- | :--- | :--- |
| `_build_link` | `_build_link(item, current_page, request)` | L43 | 1 |
| `get_menu_links` | `get_menu_links(slug, current_page, request)` | L60 | 1 |
| `menu` | `menu(context, slug, template)` | L84 | 0 |
| `NavLink.is_active` | `is_active(self)` | L30 | 0 |
| `NavLink.aria_current` | `aria_current(self)` | L34 | 0 |

### Types & Interfaces
- `type_alias DEFAULT_TEMPLATE` (L17)

## [`home/apps.py`](../home/apps.py)

### Classes
- **`class HomeConfig`** (L4)

## [`home/management/commands/seed_site.py`](../home/management/commands/seed_site.py)

### Classes
- **`class Command`** (L32)

### Functions & Methods
| Symbol | Signature | Line | Callers |
| :--- | :--- | :--- | :--- |
| `heading` | `heading(text, size)` | L16 | 1 |
| `paragraph` | `paragraph(html)` | L20 | 1 |
| `quote` | `quote(text, attribution)` | L24 | 1 |
| `cta` | `cta(text, page, url)` | L28 | 1 |
| `Command.add_arguments` | `add_arguments(self, parser)` | L35 | 0 |
| `Command.handle` | `handle(self)` | L43 | 0 |
| `Command._delete_existing` | `_delete_existing(self)` | L63 | 1 |
| `Command._delete_default_welcome_page` | `_delete_default_welcome_page(self, root)` | L71 | 1 |
| `Command._add` | `_add(self, parent, page)` | L77 | 1 |
| `Command._create_pages` | `_create_pages(self, root)` | L82 | 1 |
| `Command._configure_site` | `_configure_site(self, home)` | L169 | 1 |
| `Command._create_menus` | `_create_menus(self)` | L177 | 1 |

## [`home/migrations/0001_initial.py`](../home/migrations/0001_initial.py)

### Classes
- **`class Migration`** (L10)

## [`home/models.py`](../home/models.py)

### Classes
- **`class HomePage`** (L19)
  *Site root. Exactly one may exist, directly under the tree root.*
- **`class StandardPage`** (L85)
  *Generic content page: About, Services, etc.*
- **`class FormField`** (L108)
- **`class ContactPage`** (L112)
  *Contact form; submissions are stored and optionally emailed to `to_address`.*

### Functions & Methods
| Symbol | Signature | Line | Callers |
| :--- | :--- | :--- | :--- |
| `HomePage.hero_cta_href` | `hero_cta_href(self)` | L71 | 0 |
| `HomePage.clean` | `clean(self)` | L76 | 3 |

## [`navigation/apps.py`](../navigation/apps.py)

### Classes
- **`class NavigationConfig`** (L4)

## [`navigation/migrations/0001_initial.py`](../navigation/migrations/0001_initial.py)

### Classes
- **`class Migration`** (L9)

## [`navigation/models.py`](../navigation/models.py)

### Classes
- **`class LinkFields`** (L24)
  *A link to either an internal page or an external URL (exactly one).*
- **`class Menu`** (L92)
- **`class MenuItem`** (L114)
- **`class SubMenuItem`** (L125)

### Functions & Methods
| Symbol | Signature | Line | Callers |
| :--- | :--- | :--- | :--- |
| `LinkFields.__str__` | `__str__(self)` | L51 | 0 |
| `LinkFields.clean` | `clean(self)` | L54 | 3 |
| `LinkFields.title` | `title(self)` | L68 | 0 |
| `LinkFields.get_url` | `get_url(self, request)` | L75 | 2 |
| `LinkFields.url` | `url(self)` | L81 | 0 |
| `LinkFields.is_visible` | `is_visible(self)` | L84 | 1 |
| `Menu.__str__` | `__str__(self)` | L110 | 0 |

## [`static/js/nav.js`](../static/js/nav.js)

### Functions & Methods
| Symbol | Signature | Line | Callers |
| :--- | :--- | :--- | :--- |
| `setExpanded` | `setExpanded(button, target, expanded)` | L5 | 0 |

## [`tests/conftest.py`](../tests/conftest.py)

### Functions & Methods
| Symbol | Signature | Line | Callers |
| :--- | :--- | :--- | :--- |
| `root_page` | `root_page(db)` | L7 | 0 |
| `seeded` | `seeded(db)` | L12 | 0 |

## [`tests/test_contact_form.py`](../tests/test_contact_form.py)

### Functions & Methods
| Symbol | Signature | Line | Callers |
| :--- | :--- | :--- | :--- |
| `test_contact_form_renders_fields` | `test_contact_form_renders_fields(client, seeded)` | L8 | 0 |
| `test_valid_submission_stores_and_emails` | `test_valid_submission_stores_and_emails(client, seeded)` | L14 | 0 |
| `test_invalid_submission_shows_errors` | `test_invalid_submission_shows_errors(client, seeded)` | L30 | 0 |

## [`tests/test_menu_validation.py`](../tests/test_menu_validation.py)

### Classes
- **`class TestMenuItemValidation`** (L16)
- **`class TestCallToActionBlock`** (L59)

### Functions & Methods
| Symbol | Signature | Line | Callers |
| :--- | :--- | :--- | :--- |
| `menu` | `menu(db)` | L12 | 0 |
| `TestMenuItemValidation.test_page_and_url_both_set_is_invalid` | `test_page_and_url_both_set_is_invalid(self, menu, seeded)` | L17 | 0 |
| `TestMenuItemValidation.test_neither_page_nor_url_is_invalid` | `test_neither_page_nor_url_is_invalid(self, menu)` | L26 | 0 |
| `TestMenuItemValidation.test_external_url_requires_title` | `test_external_url_requires_title(self, menu)` | L31 | 0 |
| `TestMenuItemValidation.test_page_only_is_valid_and_title_falls_back` | `test_page_only_is_valid_and_title_falls_back(self, menu, seeded)` | L37 | 0 |
| `TestMenuItemValidation.test_explicit_title_wins` | `test_explicit_title_wins(self, menu, seeded)` | L43 | 0 |
| `TestMenuItemValidation.test_url_only_is_valid` | `test_url_only_is_valid(self, menu)` | L47 | 0 |
| `TestMenuItemValidation.test_sub_item_uses_same_validation` | `test_sub_item_uses_same_validation(self, menu, seeded)` | L52 | 0 |
| `TestCallToActionBlock.test_requires_exactly_one_target` | `test_requires_exactly_one_target(self, seeded)` | L60 | 0 |

## [`tests/test_navigation.py`](../tests/test_navigation.py)

### Classes
- **`class TestMenuRendering`** (L24)
- **`class TestActiveState`** (L52)
- **`class TestVisibility`** (L84)
- **`class TestAdmin`** (L98)

### Functions & Methods
| Symbol | Signature | Line | Callers |
| :--- | :--- | :--- | :--- |
| `main_nav` | `main_nav(html)` | L13 | 8 |
| `link` | `link(html, href)` | L17 | 5 |
| `TestMenuRendering.test_main_menu_items_and_dropdown` | `test_main_menu_items_and_dropdown(self, client, seeded)` | L25 | 0 |
| `TestMenuRendering.test_footer_menu` | `test_footer_menu(self, client, seeded)` | L34 | 0 |
| `TestMenuRendering.test_nav_landmarks` | `test_nav_landmarks(self, client, seeded)` | L40 | 0 |
| `TestMenuRendering.test_missing_menu_renders_nothing` | `test_missing_menu_renders_nothing(self, seeded)` | L45 | 0 |
| `TestActiveState.test_current_page_marked` | `test_current_page_marked(self, client, seeded)` | L53 | 0 |
| `TestActiveState.test_home_not_active_on_subpages` | `test_home_not_active_on_subpages(self, client, seeded)` | L58 | 0 |
| `TestActiveState.test_home_active_on_home` | `test_home_active_on_home(self, client, seeded)` | L62 | 0 |
| `TestActiveState.test_ancestor_highlighted_for_child_page` | `test_ancestor_highlighted_for_child_page(self, client, seeded)` | L67 | 0 |
| `TestActiveState.test_page_below_menu_item_highlights_ancestor` | `test_page_below_menu_item_highlights_ancestor(self, client, seeded)` | L74 | 0 |
| `TestVisibility.test_show_in_menus_false_hides_item` | `test_show_in_menus_false_hides_item(self, client, seeded)` | L85 | 0 |
| `TestVisibility.test_unpublished_page_hidden` | `test_unpublished_page_hidden(self, client, seeded)` | L92 | 0 |
| `TestAdmin.test_menu_snippet_edit_view_with_nested_inline` | `test_menu_snippet_edit_view_with_nested_inline(self, client, seeded)` | L99 | 0 |

## [`tests/test_pages.py`](../tests/test_pages.py)

### Classes
- **`class TestParentChildRules`** (L12)
- **`class TestHomePageValidation`** (L49)
- **`class TestSeedAndRendering`** (L64)

### Functions & Methods
| Symbol | Signature | Line | Callers |
| :--- | :--- | :--- | :--- |
| `TestParentChildRules.test_home_page_only_at_root` | `test_home_page_only_at_root(self, seeded, root_page)` | L13 | 0 |
| `TestParentChildRules.test_home_page_max_count` | `test_home_page_max_count(self, seeded, root_page)` | L18 | 0 |
| `TestParentChildRules.test_home_page_can_be_created_on_empty_root` | `test_home_page_can_be_created_on_empty_root(self, root_page)` | L22 | 0 |
| `TestParentChildRules.test_standard_page_under_home_and_standard` | `test_standard_page_under_home_and_standard(self, seeded, root_page)` | L30 | 0 |
| `TestParentChildRules.test_contact_page_rules` | `test_contact_page_rules(self, seeded)` | L36 | 0 |
| `TestParentChildRules.test_contact_page_not_under_standard_page` | `test_contact_page_not_under_standard_page(self, seeded)` | L43 | 0 |
| `TestHomePageValidation.test_cta_page_and_url_conflict` | `test_cta_page_and_url_conflict(self, seeded)` | L50 | 0 |
| `TestHomePageValidation.test_cta_text_without_link` | `test_cta_text_without_link(self, seeded)` | L56 | 0 |
| `TestSeedAndRendering.test_seed_creates_tree` | `test_seed_creates_tree(self, seeded)` | L65 | 0 |
| `TestSeedAndRendering.test_seed_is_idempotent` | `test_seed_is_idempotent(self, seeded)` | L71 | 0 |
| `TestSeedAndRendering.test_seed_force_recreates` | `test_seed_force_recreates(self, seeded)` | L77 | 0 |
| `TestSeedAndRendering.test_pages_render` | `test_pages_render(self, client, seeded, path)` | L85 | 0 |
| `TestSeedAndRendering.test_seo_fields_rendered` | `test_seo_fields_rendered(self, client, seeded)` | L90 | 0 |
| `TestSeedAndRendering.test_stream_blocks_rendered` | `test_stream_blocks_rendered(self, client, seeded)` | L95 | 0 |
