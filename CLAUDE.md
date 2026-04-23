# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Django Full App — Full Django 5.2 blog + accounts application with authentication, crispy forms, DRF API, class-based views, and split dev/prod settings.

Built with Django 5.2, Python 3.13, Django REST Framework, and SQLite (dev) / PostgreSQL (prod).

## Commands

```bash
pip install -r requirements.txt          # Install dependencies
cp .env.example .env                     # Set up environment
python manage.py migrate                 # Apply migrations
python manage.py runserver               # Start dev server (http://localhost:8000)
python -m pytest                         # Run tests (pytest + pytest-django)
python -m pytest --cov                   # Tests with coverage
ruff check .                             # Lint
ruff format .                            # Format
```

## Environment

Copy `.env.example` to `.env`. Dev mode uses SQLite by default — no database setup needed.

## Architecture

- `config/settings/` — Split settings: `base.py` (shared), `dev.py` (SQLite, debug), `prod.py` (Postgres, SSL)
- `apps/accounts/` — User auth: login, signup, logout, profile, custom user signals
- `apps/blog/` — Blog CRUD: posts, categories, DRF API viewsets, RSS feed
- `apps/*/tests/` — pytest test files with factory-boy fixtures
- `conftest.py` — Shared pytest fixtures (api_client, auth_client)

## Rules

- Always create migrations for model changes
- Use class-based views for CRUD, function views for simple endpoints
- Parameterized queries only — never raw SQL with string interpolation
- All new models need proper `__str__` and `Meta.ordering`
- Settings: use `os.environ.get()` with sensible defaults — never crash on missing env vars
- Tests: use pytest + factory-boy, not Django TestCase
