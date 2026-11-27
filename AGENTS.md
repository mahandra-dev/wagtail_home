# Agent Instructions & Codebase Guidelines

Welcome to **wagtail-home**. This file gives AI agents and automated tools the verified commands,
architecture map and operating constraints for this repository.

---

## 1. Project Overview
- **Repository Purpose**: A small, production-ready-ish CMS site on Wagtail 7.4 LTS with three page
  types (Home, Standard, Contact form), shared StreamField blocks and admin-editable menus
  (one dropdown level) rendered by a `{% menu %}` template tag.
- **Core Languages & Frameworks**: Python 3.12, Django 5.2 LTS, Wagtail 7.4 LTS, PostgreSQL 17
  (psycopg 3), django-environ, WhiteNoise, gunicorn. Plain CSS/JS frontend (no frameworks).
- **Primary Runtime / Environment**: `uv`-managed venv in `.venv/` (Python pinned in
  `.python-version`), Postgres in Docker (`docker compose`), config from env vars / `.env`.

---

## 2. Essential Commands

> [!IMPORTANT]
> Run all commands from the repository root. The `Makefile` is the single entry point; every
> Python command goes through `uv run`. **Never use pip, venv or requirements.txt** — add
> packages with `uv add <pkg>` (dev tools: `uv add --dev <pkg>`).

### Build & Setup
```bash
# First-time bootstrap: .env + uv sync + Postgres container + migrate + seed demo site
make setup

# Install / sync dependencies only
make install            # = uv sync

# Run the dev server (http://localhost:8000, admin at /admin/)
make run                # override port: make run PORT=8010

# Schema changes
make migrations && make migrate

# Whole stack in Docker (web + db)
make build && make up
```

### Testing & Verification
```bash
# Run all tests (needs Postgres up: make db-up)
make test               # = uv run pytest

# Run a single test file / test
uv run pytest tests/test_navigation.py
make test ARGS="-k menu -x"

# Linting & Formatting
make lint               # ruff check . && ruff format --check .
make format             # ruff format . && ruff check --fix .

# Django system checks (also check --deploy against prod settings with dummy secrets)
make check

# Everything CI runs
make ci                 # lint + test + check
```

There is no static type checker configured; `make check` (Django system checks) is the
closest equivalent and must pass.

---

## 3. Architecture & Context Navigation

For in-depth details, see the [`context/`](./context/) directory:

- [**context/index.md**](./context/index.md): Documentation map and quick index.
- [**context/architecture.md**](./context/architecture.md): System design, layers, request lifecycle.
- [**context/modules.md**](./context/modules.md): Module catalog with public interfaces.
- [**context/signatures.md**](./context/signatures.md): Generated index of all signatures.
- [**context/dependencies.md**](./context/dependencies.md): Internal import graph and third-party packages.
- [**context/conventions.md**](./context/conventions.md): Code style, validation patterns, tests, invariants.

### Key Entry Points & Hub Modules
| Component / File | Role | Type |
| :--- | :--- | :--- |
| `manage.py` | Django CLI entry (defaults to `config.settings.dev`) | Entrypoint |
| `config/wsgi.py` | WSGI app served by gunicorn in the Docker image (`config.settings.prod`) | Entrypoint |
| `config/urls.py` | URL routing; Wagtail page serving is the last catch-all | Entrypoint |
| `home/management/commands/seed_site.py` | `seed_site` command: demo page tree + `main`/`footer` menus | Entrypoint |
| `navigation/models.py` | `Menu` snippet, `MenuItem`, `SubMenuItem`, `LinkFields` (in-degree 5) | Core Hub |
| `home/models.py` | `HomePage`, `StandardPage`, `ContactPage`, `FormField` | Core Hub |
| `core/blocks.py` | Shared StreamField blocks (`BaseStreamBlock`) | Core Hub |
| `core/templatetags/navigation_tags.py` | `{% menu %}` tag, `NavLink`, active-state logic | Core Hub |
| `config/settings/base.py` | Shared settings, all env-driven | Core Hub |

---

## 4. Agent Rules & Operational Constraints

Follow these rules on every task:

1. **Surgical Changes**: Touch only files needed for the task. Don't reformat unrelated code.
2. **Never Break Tests or Checks**: Run `make lint`, `make test` and `make check` (or `make ci`)
   before finishing. Tests need Postgres (`make db-up`).
3. **uv only**: Dependencies live in `pyproject.toml` + `uv.lock` (committed). Use `uv add`,
   `uv lock`, `uv run`. Never pip or `requirements.txt`.
4. **Migrations**: Any model change needs a migration (`make migrations`); commit it with the
   model change. Migrations are excluded from ruff.
5. **Preserve Existing Patterns** (see [context/conventions.md](./context/conventions.md)):
   - "Page **or** external URL, exactly one" validation lives in `clean()` (models) or
     `StructBlock.clean()` (blocks) and raises field-keyed errors.
   - New body content types go into `core/blocks.py` `BaseStreamBlock` with a template under
     `templates/blocks/`.
   - Menus are rendered only via `{% menu "<slug>" %}`; menu nesting stays at one level
     (`MenuItem` → `SubMenuItem`), no self-referencing FK.
   - No third-party menu packages; no frontend frameworks.
6. **Secrets**: All config comes from env vars (`config/settings/base.py`). Never commit `.env`
   or real secrets; add new variables to `.env.example`.
7. **No Speculative Abstractions**: Solve only the immediate problem.

---

## 5. Automatic Context & Graph Maintenance (Post-Change Instruction)

> [!IMPORTANT]
> **Always Keep Context & Symbol Graphs In Sync**:
> If code was created, modified, or deleted during your task, refresh the symbol graph and
> context artifacts. The scripts belong to the `codebase-context-generator` skill
> (installed at `~/.claude/skills/codebase-context-generator`); `.context_cache/` is git-ignored.

```bash
S=~/.claude/skills/codebase-context-generator/scripts

# 1. Rescan AST and update symbol/call graphs
python3 $S/ast_scanner.py --root .
python3 $S/dependency_graph.py --manifest .context_cache/ast_manifest.json
python3 $S/symbol_graph.py \
  --manifest .context_cache/ast_manifest.json \
  --save-graph .context_cache/symbol_graph.json \
  --export-signatures context/signatures.md

# 2. Update context docs if public APIs, modules, or architecture changed:
#    - new modules            -> context/modules.md
#    - architecture/data flow -> context/architecture.md
#    - new dependencies       -> context/dependencies.md

# 3. Verify documentation integrity
python3 $S/verify_context.py --root .
```

Quick symbol lookup (after step 1):

```bash
python3 $S/symbol_graph.py --find "get_menu_links"
python3 $S/symbol_graph.py --callers "is_visible"
python3 $S/symbol_graph.py --callees "_create_pages"
```

If delegating to a subagent, use this prompt:
> *"Code changes were completed in the workspace. Run the codebase-context-generator scripts to
> refresh the AST manifest, symbol graph, and `context/signatures.md`. If new files or
> architectural components were introduced, update `context/modules.md` and
> `context/architecture.md`, then run `verify_context.py` to ensure 0 broken links and full
> coverage."*
