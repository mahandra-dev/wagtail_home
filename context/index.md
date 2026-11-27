# Codebase Context & Navigation

Structured technical documentation for **wagtail-home**: architecture, modules, dependencies and
engineering conventions. Start with [../AGENTS.md](../AGENTS.md) for commands and rules.

## Navigation Map

1. [System Architecture](./architecture.md) — layers, Mermaid diagram, request lifecycle, menu rendering flow.
2. [Module Catalog](./modules.md) — app-by-app breakdown of models, blocks, template tags, commands, templates.
3. [Signatures & Symbol Index](./signatures.md) — generated function/method signatures and locations.
4. [Dependencies & Integrations](./dependencies.md) — internal import graph, third-party packages, external services.
5. [Engineering Conventions](./conventions.md) — style, validation patterns, testing, invariants.

## Quick Facts
- **Total Source Files**: 34 scanned (33 Python, 1 JavaScript) plus 17 Django templates and 1 CSS file; ~1.9k LOC.
- **Primary Languages**: Python 3.12 (Django 5.2 / Wagtail 7.4), Django templates, vanilla JS/CSS.
- **Key Entrypoint**: [`manage.py`](../manage.py) (CLI), [`config/wsgi.py`](../config/wsgi.py) (gunicorn), [`config/urls.py`](../config/urls.py) (routing).
- **Django apps**: [`core`](../core/), [`home`](../home/), [`navigation`](../navigation/); project package [`config`](../config/).
- **Tests**: [`tests/`](../tests/) — pytest-django, 41 tests, real PostgreSQL.
