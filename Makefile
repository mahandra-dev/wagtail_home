# Single entry point for routine tasks. Every Python command runs through `uv run`.
# Works with GNU make on Linux and the stock make on macOS.

UV       ?= uv
MANAGE    = $(UV) run python manage.py
DC       ?= docker compose
SETTINGS ?= config.settings.dev
SERVICE  ?= web
ARGS     ?=
FILE     ?=
FORCE    ?=
PORT     ?= 8000

# Settings module for every manage.py / pytest call (overridable: make run SETTINGS=...).
export DJANGO_SETTINGS_MODULE := $(SETTINGS)

# Throwaway values so `check --deploy` can run without real secrets.
CHECK_ENV = DJANGO_SECRET_KEY=check-deploy-dummy-key-0123456789-abcdefghijklmnopqrstuvwxyz \
            DJANGO_ALLOWED_HOSTS=example.com

TIMESTAMP := $(shell date +%Y%m%d-%H%M%S)
BACKUP_DIR = backups

.DEFAULT_GOAL := help

.PHONY: help install env setup \
        run shell superuser \
        migrations migrate seed db-up db-down db-shell db-reset dump restore \
        lint format test cov check ci \
        collectstatic update-index fixtree \
        up down build logs dc-shell dc-migrate dc-seed dc-superuser dc-test \
        lock upgrade clean

##@ Setup

help: ## Show this help
	@awk 'BEGIN {FS = ":.*## "} \
		/^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5); next } \
		/^[a-zA-Z0-9_-]+:.*## / { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@echo ""

install: ## Install all dependencies incl. dev (uv sync)
	$(UV) sync

env: ## Create .env from .env.example if missing (never overwrites)
	@if [ -f .env ]; then echo ".env already exists, leaving it untouched."; \
	else cp .env.example .env && echo "Created .env from .env.example"; fi

setup: ## First-time bootstrap: env + install + db-up + migrate + seed
	@$(MAKE) --no-print-directory env
	@$(MAKE) --no-print-directory install
	@$(MAKE) --no-print-directory db-up
	@$(MAKE) --no-print-directory migrate
	@$(MAKE) --no-print-directory seed

##@ Run

run: ## Run the dev server on 0.0.0.0:8000 (override: PORT=...)
	$(MANAGE) runserver 0.0.0.0:$(PORT)

shell: ## Django shell
	$(MANAGE) shell

superuser: ## Create an admin user
	$(MANAGE) createsuperuser

##@ Database

migrations: ## Create new migrations (makemigrations)
	$(MANAGE) makemigrations $(ARGS)

migrate: ## Apply migrations
	$(MANAGE) migrate $(ARGS)

seed: ## Seed demo pages and menus (seed_site; ARGS=--force to recreate)
	$(MANAGE) seed_site $(ARGS)

db-up: ## Start only the Postgres container (waits until healthy)
	$(DC) up -d --wait db

db-down: ## Stop the Postgres container
	$(DC) stop db

db-shell: ## psql inside the db container
	$(DC) exec db sh -c 'psql -U "$$POSTGRES_USER" -d "$$POSTGRES_DB"'

db-reset: ## Drop & recreate the DB, migrate, seed (confirm, or FORCE=1)
	@if [ "$(FORCE)" != "1" ]; then \
		printf "This will DESTROY all data in the database. Continue? [y/N] "; \
		read answer; \
		case "$$answer" in [yY]|[yY][eE][sS]) ;; *) echo "Aborted."; exit 1 ;; esac; \
	fi
	$(DC) exec -T db sh -c 'dropdb -U "$$POSTGRES_USER" --if-exists --force "$$POSTGRES_DB" && createdb -U "$$POSTGRES_USER" "$$POSTGRES_DB"'
	@$(MAKE) --no-print-directory migrate
	@$(MAKE) --no-print-directory seed

dump: ## pg_dump to backups/db-<timestamp>.dump
	@mkdir -p $(BACKUP_DIR)
	$(DC) exec -T db sh -c 'pg_dump -U "$$POSTGRES_USER" -d "$$POSTGRES_DB" -Fc' > $(BACKUP_DIR)/db-$(TIMESTAMP).dump
	@echo "Saved $(BACKUP_DIR)/db-$(TIMESTAMP).dump"

restore: ## pg_restore from a dump (FILE=backups/db-....dump)
	@if [ -z "$(FILE)" ]; then echo "Usage: make restore FILE=backups/<name>.dump"; exit 1; fi
	@if [ ! -f "$(FILE)" ]; then echo "File not found: $(FILE)"; exit 1; fi
	$(DC) exec -T db sh -c 'pg_restore -U "$$POSTGRES_USER" -d "$$POSTGRES_DB" --clean --if-exists --no-owner' < "$(FILE)"

##@ Quality

lint: ## Lint with ruff (check + format check)
	$(UV) run ruff check .
	$(UV) run ruff format --check .

format: ## Format code and apply autofixes
	$(UV) run ruff format .
	$(UV) run ruff check --fix .

test: ## Run tests (extra args: ARGS="-k menu -x")
	$(UV) run pytest $(ARGS)

cov: ## Run tests with coverage (terminal + htmlcov/)
	$(UV) run pytest --cov --cov-report=term-missing --cov-report=html $(ARGS)

check: ## Django system checks + check --deploy with prod settings
	$(MANAGE) check
	$(CHECK_ENV) $(MANAGE) check --deploy --fail-level WARNING --settings=config.settings.prod

ci: ## What CI runs: lint + test + check
	@$(MAKE) --no-print-directory lint
	@$(MAKE) --no-print-directory test
	@$(MAKE) --no-print-directory check

##@ Static & Wagtail

collectstatic: ## Collect static files
	$(MANAGE) collectstatic --noinput

update-index: ## Rebuild the Wagtail search index
	$(MANAGE) update_index

fixtree: ## Repair the Wagtail page tree
	$(MANAGE) fixtree

##@ Docker

up: ## docker compose up -d
	$(DC) up -d

down: ## docker compose down
	$(DC) down

build: ## Rebuild images
	$(DC) build

logs: ## Follow logs (SERVICE=web|db)
	$(DC) logs -f $(SERVICE)

dc-shell: ## bash in the web container
	$(DC) exec web bash

dc-migrate: ## migrate inside the web container
	$(DC) exec web uv run --frozen --no-sync python manage.py migrate

dc-seed: ## seed_site inside the web container
	$(DC) exec web uv run --frozen --no-sync python manage.py seed_site $(ARGS)

dc-superuser: ## createsuperuser inside the web container
	$(DC) exec web uv run --frozen --no-sync python manage.py createsuperuser

dc-test: ## pytest inside the web container
	$(DC) exec -T web uv run --frozen --no-sync pytest $(ARGS)

##@ Maintenance

lock: ## Update uv.lock from pyproject.toml
	$(UV) lock

upgrade: ## Upgrade all locked dependencies, then sync
	$(UV) lock --upgrade
	$(UV) sync

clean: ## Remove caches and coverage artefacts
	find . -path ./.venv -prune -o -type d -name __pycache__ -exec rm -rf {} +
	rm -rf .pytest_cache .ruff_cache htmlcov .coverage coverage.xml
