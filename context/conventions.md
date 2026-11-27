# Engineering Conventions & Invariants

## 1. Code Style & Naming
- **Formatter / linter**: ruff (`line-length = 100`, `target-version = py312`, double quotes);
  rules `E W F I B UP DJ SIM C4 RUF`, ignoring `RUF012` (mutable Wagtail class attrs like
  `panels`, `search_fields`) and `RUF005` (`Page.content_panels + [...]` is idiomatic).
  Migrations are excluded. First-party packages for isort: `config core home navigation`.
- **Files / modules**: `snake_case`. Templates: `templates/<app>/<model_snake>.html`,
  `templates/blocks/<block>.html`.
- **Classes**: `PascalCase` (`HomePage`, `CallToActionBlock`, `NavLink`).
- **Functions / methods**: `snake_case`; module-private helpers prefixed `_`
  (`_build_link`, `_create_pages`).
- **Constants**: `UPPER_SNAKE_CASE` (`DEFAULT_TEMPLATE`, Django settings).
- **Wagtail idioms**: `content_panels = Page.content_panels + [...]`,
  `search_fields = Page.search_fields + [...]`, `StreamField(BaseStreamBlock(), blank=True,
  use_json_field=True)`, `verbose_name` in `Meta`, `related_name="+"` for one-way FKs.
- Docstrings explain *why* (design decisions), not what.

## 2. Validation & Error Handling Pattern
Validation is done at the model/block layer, never in views or templates, and errors are keyed
to the offending fields so the Wagtail admin highlights them.

```python
# Models: override clean(), call super(), raise field-keyed ValidationError
def clean(self):
    super().clean()
    if has_page and has_url:
        msg = "Choose either a page or an external URL, not both."
        raise ValidationError({"link_page": msg, "link_url": msg})

# StructBlocks: override clean(value), raise StructBlockValidationError
raise StructBlockValidationError(
    block_errors={"page": ErrorList([ValidationError(msg)]), "url": ErrorList([...])}
)
```

Rendering code degrades gracefully instead of raising: an unknown menu slug renders nothing,
hidden/unpublished pages are skipped, a missing `page` in context disables active state.

## 3. Testing Strategy
- **Location**: top-level `tests/`, files `test_*.py`; pytest-django with
  `DJANGO_SETTINGS_MODULE=config.settings.dev`, `--reuse-db --strict-markers -ra`.
- **Database**: real PostgreSQL (no SQLite, no mocks). Start it with `make db-up`.
- **Fixtures** (`tests/conftest.py`): `root_page`, `seeded` (runs `seed_site` and returns
  `{slug: specific_page}`). Prefer `seeded` over hand-built trees.
- **Style**: module-level `pytestmark = pytest.mark.django_db`; group by `class TestX`;
  assert on rendered HTML via the Django `client` and small regex helpers; email via
  `django.core.mail.outbox`.
- **Commands**: `make test`, `make test ARGS="-k navigation -x"`, `make cov`, `make ci`.

## 4. Critical Invariants (Do Not Break)
- **Exactly one link target**: `LinkFields`, `CallToActionBlock` and `HomePage` hero CTA accept
  a page **or** an external URL, never both; external menu links require a title.
- **Page tree rules**: `HomePage` only under the tree root, `max_count=1`; `StandardPage` under
  HomePage/StandardPage; `ContactPage` only under HomePage, `max_count=1`, no children.
- **Menus**: one nesting level by schema (`Menu` → `MenuItem` → `SubMenuItem`); no `parent` FK,
  no third-party menu packages. Menus are looked up by `slug` (`main`, `footer` are used in
  `base.html`).
- **Menu visibility**: page links hidden unless the page is `live` and `show_in_menus`.
- **Active state / accessibility**: `aria-current="page"` for the current page,
  `aria-current="true"` + `is-active` for ancestors; site roots (depth ≤ 2) only on exact match.
  Keep `nav` landmarks with `aria-label="Main"` / `"Footer"`, external new-tab links with
  `rel="noopener noreferrer"`.
- **Performance**: `get_menu_links` must keep its `prefetch_related` on items, sub-items and
  linked pages (no N+1 per request).
- **URL order**: Wagtail's `include(wagtail_urls)` must stay the last pattern in `config/urls.py`.
- **Config & secrets**: every environment-dependent value comes from env vars via
  `django-environ`; `.env` is git-ignored, new variables go into `.env.example`.
  `make check` (incl. `check --deploy --fail-level WARNING` on prod settings) must pass.
- **Tooling**: uv only (`uv add`, `uv run`, `uv.lock` committed); no pip / requirements.txt.
  Every Python command in the `Makefile` runs via `$(UV) run`; targets must work on Linux and
  macOS make.
- **`seed_site`** stays atomic and idempotent (no-op if a HomePage exists unless `--force`);
  tests depend on its exact slugs and menu contents.
