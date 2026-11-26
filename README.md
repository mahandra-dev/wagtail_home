# Wagtail Home

A small, production-ready-ish [Wagtail 7.4 LTS](https://docs.wagtail.org/en/stable/releases/7.4.html) site on
Django 5.2 LTS and PostgreSQL 17, with admin-editable menus (including dropdowns), a contact form
and shared StreamField blocks.

- **Python** 3.12 (pinned in `.python-version`)
- **Dependencies & virtualenv:** [uv](https://docs.astral.sh/uv/) only — `pyproject.toml` + `uv.lock`
- **Database:** PostgreSQL 17 via psycopg 3
- **Config:** environment variables (`django-environ`), see `.env.example`

## Quick start

Requirements: `uv` and Docker (for PostgreSQL).

```bash
make setup && make superuser && make run
```

Open http://localhost:8000 (site) and http://localhost:8000/admin/ (Wagtail admin).

`make setup` creates `.env` from `.env.example`, installs dependencies (`uv sync`), starts the
Postgres container, applies migrations and seeds the demo site.

> Ports 5432 or 8000 already taken? Change `POSTGRES_PORT` (and the port in `DATABASE_URL`) and
> `WEB_PORT` in `.env`; for the local dev server use `make run PORT=8010`.

## Everything via `make`

The `Makefile` is the single entry point; every Python command runs through `uv run`.
Run `make` (or `make help`) to list all targets.

| Area | Targets |
|---|---|
| Setup | `help`, `install`, `env`, `setup` |
| Run | `run` (`PORT=`), `shell`, `superuser` |
| Database | `migrations`, `migrate`, `seed` (`ARGS=--force`), `db-up`, `db-down`, `db-shell`, `db-reset` (`FORCE=1`), `dump`, `restore FILE=...` |
| Quality | `lint`, `format`, `test` (`ARGS=`), `cov`, `check`, `ci` |
| Static & Wagtail | `collectstatic`, `update-index`, `fixtree` |
| Docker | `up`, `down`, `build`, `logs` (`SERVICE=`), `dc-shell`, `dc-migrate`, `dc-seed`, `dc-superuser`, `dc-test` |
| Maintenance | `lock`, `upgrade`, `clean` |

Common variables: `SETTINGS` (default `config.settings.dev`), `UV`, `DC`.

Examples:

```bash
make test ARGS="-k navigation -x"
make dump                                  # -> backups/db-YYYYmmdd-HHMMSS.dump
make restore FILE=backups/db-20260101-120000.dump
make db-reset FORCE=1                      # no confirmation prompt
make run SETTINGS=config.settings.prod     # any target with other settings
```

## Without make

```bash
cp .env.example .env
uv sync
docker compose up -d --wait db
uv run python manage.py migrate
uv run python manage.py seed_site
uv run python manage.py createsuperuser
uv run python manage.py runserver
uv run pytest
uv run ruff check . && uv run ruff format --check .
```

## Docker

```bash
docker compose up --build        # or: make build && make up
```

- `db`: `postgres:17` with a healthcheck and a named volume.
- `web`: built from `Dockerfile` (uv binary copied from `ghcr.io/astral-sh/uv`, `uv sync --frozen`,
  venv in `/opt/venv`). Compose runs it with dev settings: `migrate` then `runserver` on port 8000,
  with the source bind-mounted for live reload.
- The image's default `CMD` is gunicorn with `config.settings.prod` (for real deployments).

Seed the demo content and create an admin inside the container:

```bash
make dc-seed && make dc-superuser
```

## Project layout

```
config/            settings (base/dev/prod), urls, wsgi/asgi
core/              shared StreamField blocks, {% menu %} template tag
home/              HomePage, StandardPage, ContactPage, seed_site command
navigation/        Menu snippet, MenuItem, SubMenuItem
templates/         base.html, page templates, block templates, menu templates
static/            css/site.css, js/nav.js
tests/             pytest-django test suite
```

## Pages

| Page | Parent | Notes |
|---|---|---|
| `HomePage` | root | `max_count = 1`; hero (title, subtitle, image, CTA page or URL) + body |
| `StandardPage` | HomePage, StandardPage | intro + body (About, Services, ...) |
| `ContactPage` | HomePage | `AbstractEmailForm`, `max_count = 1`; form fields, landing text, email settings |

Body blocks (`core/blocks.py`): heading, rich text paragraph, image with caption, quote,
call-to-action (page **or** external URL), raw HTML embed.

SEO: `seo_title` and `search_description` from the Promote tab are rendered in `<title>` and
`<meta name="description">`.

## Menus

Menus are snippets (**Snippets → Menus** in the admin), identified by `slug`:

```
Menu (title, slug)
 └── MenuItem      link_title, link_page | link_url, open_in_new_tab
      └── SubMenuItem   same fields — one dropdown level
```

- Exactly one of *page* / *external URL* is required; external links also need a title.
  An empty title falls back to the page title.
- Items linking to unpublished pages or pages with **Show in menus** unchecked are hidden.
- Nesting uses a nested inline (`SubMenuItem` inside `MenuItem`) instead of a self-referencing
  `parent` FK: editors manage dropdown children right inside the parent item, and the schema
  makes deeper nesting or cycles impossible.

Render in templates:

```django
{% load navigation_tags %}
{% menu "main" %}
{% menu "footer" template="navigation/footer_menu.html" %}
```

Active state: the current page gets `aria-current="page"`; a menu item whose page is an ancestor
of the current page (or whose dropdown contains it) gets `aria-current="true"` and `is-active`.
The site root (Home) is only active on an exact match.

## Configuration

All settings come from environment variables (or `.env`, which is git-ignored). See
`.env.example` for the full list. Required in production:

- `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS`
- `DATABASE_URL`, `EMAIL_URL`, `WAGTAILADMIN_BASE_URL`

Production settings (`config.settings.prod`) enable HTTPS redirect, HSTS, secure cookies and
WhiteNoise compressed/manifest static files. TLS is expected to terminate at a reverse proxy that
sets `X-Forwarded-Proto`. `make check` runs `check --deploy` against them with dummy secrets.
