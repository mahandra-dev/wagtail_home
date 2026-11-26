# Task: Bootstrap a Wagtail 7.4 LTS site on PostgreSQL

Create a new, production-ready-ish Wagtail project in the current directory. Work step by step: first show me a short plan (file tree + models), then implement, then run checks and tests.

## Stack
- Python 3.12+
- **Environment & dependencies: `uv` only.** Do NOT use pip, venv, poetry or requirements.txt.
  - `uv init` / `pyproject.toml` as the single source of dependencies, `uv.lock` committed
  - Virtual env in `.venv/` created by `uv venv` / `uv sync`; `.venv` git-ignored
  - Add packages with `uv add` (dev tools with `uv add --dev`: ruff, pytest, pytest-django)
  - Run everything via `uv run` (e.g. `uv run python manage.py migrate`, `uv run pytest`, `uv run ruff check .`)
  - Pin Python version with `.python-version`
- Wagtail `>=7.4,<7.5` (LTS). Use the Django version officially supported by Wagtail 7.4 — check the Wagtail compatibility table, don't guess.
- PostgreSQL 17 via `psycopg[binary]` (psycopg 3)
- Config via environment variables (`django-environ`), `.env.example` committed, `.env` git-ignored
- Docker Compose: `db` (postgres:17) + `web`. The `web` Dockerfile must also use uv (official `ghcr.io/astral-sh/uv` image or copy the uv binary), install with `uv sync --frozen`, and run via `uv run`. Must also run locally without Docker.

## Project structure
- Project package: `config/` (settings split into `base.py`, `dev.py`, `prod.py`)
- Apps: `home/` (pages), `navigation/` (menus), `core/` (shared blocks, templatetags)
- Templates in `templates/`, static in `static/`

## Page models
1. **HomePage** — hero (title, subtitle, image, CTA link), body `StreamField`. Only one allowed at the root (`max_count = 1`).
2. **StandardPage** — generic content page (About, Services, etc.): intro, body `StreamField`. Allowed under HomePage and StandardPage.
3. **ContactPage** — based on Wagtail `AbstractEmailForm` (fields: name, email, message), landing text, email-to settings. `max_count = 1`.

Shared StreamField blocks in `core/blocks.py`: heading, rich text paragraph, image with caption, quote, call-to-action (page or external URL), raw embed.

All pages: SEO fields (`search_description`, `seo_title` from Wagtail promote panel), `show_in_menus` respected.

## Menus (main requirement)
Editable from the Wagtail admin, no third-party menu packages:
- `navigation.models.Menu` — snippet with `title` and `slug` (e.g. `main`, `footer`).
- `MenuItem` — `Orderable` inline on Menu: `link_title`, `link_page` (optional PageChooser), `link_url` (optional external URL), `open_in_new_tab`. Validate: exactly one of page/URL. If `link_title` empty, use page title.
- Support one level of nested items (dropdown) via a `parent` relation or a separate sub-items inline — choose the simpler clean approach and explain it.
- Template tag `{% menu "main" %}` in `core/templatetags/navigation_tags.py`, highlights the active item (current page or its ancestor).
- Data migration / management command `seed_site` that creates: HomePage, About, Services (with 2 child pages), Contact, plus a `main` menu (Home, About, Services ▸ child1/child2, Contact) and a `footer` menu.

## Templates
- `base.html` with header (main menu, responsive mobile toggle — plain CSS/JS, no frameworks), footer (footer menu), `{% block content %}`.
- Templates for each page type and each StreamField block.
- Minimal clean CSS, semantic HTML, accessible (nav landmarks, `aria-current` on active item).

## Quality
- `ruff` (lint + format) config in `pyproject.toml`
- Tests (`pytest-django` or Django test runner): page creation and parent/child rules, menu rendering + active state, MenuItem validation, contact form submission.
- `python manage.py check --deploy` must pass with prod settings (except things that genuinely need real secrets/HTTPS).
- README commands use `uv` (`uv sync`, `uv run python manage.py ...`, `uv run pytest`) — no pip instructions anywhere.

## Makefile
Create a `Makefile` as the single entry point for all routine commands. Every Python command goes through `uv run`. Requirements:
- `.PHONY` for all targets, `help` as the default target (auto-generated from `## comments` next to each target)
- Variables at the top: `UV ?= uv`, `MANAGE = $(UV) run python manage.py`, `DC ?= docker compose`, `SETTINGS ?= config.settings.dev`
- Targets must work on Linux and macOS (no GNU-only flags without a fallback)

Targets:

**Setup**
- `help` — list all targets with descriptions
- `install` — `uv sync` (incl. dev deps)
- `env` — copy `.env.example` → `.env` if missing (never overwrite)
- `setup` — `env` + `install` + `db-up` + `migrate` + `seed` (first-time bootstrap)

**Run**
- `run` — dev server on `0.0.0.0:8000`
- `shell` — Django shell
- `superuser` — `createsuperuser`

**Database**
- `migrations` — `makemigrations`
- `migrate` — `migrate`
- `seed` — `seed_site` management command
- `db-up` / `db-down` — start/stop only the Postgres container
- `db-shell` — `psql` inside the db container
- `db-reset` — drop & recreate the DB, migrate, seed (ask for confirmation unless `FORCE=1`)
- `dump` / `restore` — `pg_dump` / `pg_restore` to/from `backups/` with timestamped filenames (`FILE=` param for restore)

**Quality**
- `lint` — `ruff check .`
- `format` — `ruff format .` + `ruff check --fix .`
- `test` — `pytest` (pass extra args via `ARGS=`)
- `cov` — tests with coverage report
- `check` — `manage.py check` + `check --deploy` with prod settings
- `ci` — `lint` + `test` + `check` (what CI should run)

**Static & Wagtail**
- `collectstatic` — `collectstatic --noinput`
- `update-index` — Wagtail `update_index`
- `fixtree` — Wagtail `fixtree`

**Docker**
- `up` / `down` — `docker compose up -d` / `down`
- `build` — rebuild images
- `logs` — follow logs (`SERVICE=` param, default `web`)
- `dc-shell` — bash in the `web` container
- `dc-migrate`, `dc-seed`, `dc-superuser`, `dc-test` — same as local targets but executed inside the `web` container

**Maintenance**
- `lock` — `uv lock`
- `upgrade` — `uv lock --upgrade` then `uv sync`
- `clean` — remove `__pycache__`, `.pytest_cache`, `.ruff_cache`, `htmlcov`, `.coverage`

README must document the Makefile as the primary way to work with the project (Quick start: `make setup && make superuser && make run`).


## Acceptance criteria
- `docker compose up` → site at http://localhost:8000, admin at /admin/
- `python manage.py seed_site` produces a navigable site with working main + footer menus including the dropdown
- All tests pass, ruff is clean
- No secrets in the repo
- `make setup && make run` works on a clean machine with only uv and Docker installed; `make ci` passes.


When done, give me a short summary: file tree, commands to run, and any decisions you made that I should review.