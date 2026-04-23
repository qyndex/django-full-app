# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Django Full App -- a production-ready blog + accounts application with real authentication, database-backed content, DRF API, class-based views, and crispy Bootstrap 5 forms.

Built with Django 5.2, Python 3.13, Django REST Framework, and SQLite (dev) / PostgreSQL (prod).

## Quick Start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_data        # 5 users, 10 posts, 15 comments, 5 categories
python manage.py runserver         # http://localhost:8000
```

Demo credentials after seeding:
- **Admin**: admin / admin1234
- **Users**: alice, bob, carol, dave, eve / demo1234

## Commands

```bash
python manage.py migrate                 # Apply migrations
python manage.py seed_data               # Seed demo data (safe to re-run)
python manage.py seed_data --flush       # Reset and re-seed
python manage.py createsuperuser         # Create admin manually
python manage.py runserver               # Dev server (localhost:8000)
python -m pytest                         # Run tests (pytest + pytest-django)
python -m pytest --cov                   # Tests with coverage
ruff check .                             # Lint
ruff format .                            # Format
```

## Environment

Copy `.env.example` to `.env`. Dev mode uses SQLite -- no database setup needed.

Key env vars:
- `DJANGO_SETTINGS_MODULE` -- `config.settings.dev` (default) or `config.settings.prod`
- `DJANGO_SECRET_KEY` -- auto-generated in dev, required in prod
- `DATABASE_URL` -- Postgres connection string (prod only)
- `SECURE_SSL_REDIRECT` -- set `true` when behind SSL-terminating load balancer

## Architecture

```
config/
  settings/base.py      Shared settings (installed apps, middleware, DRF, crispy)
  settings/dev.py       SQLite, DEBUG=True, console email
  settings/prod.py      Postgres via DATABASE_URL, SSL, SMTP email
  urls.py               Root URL conf: admin + accounts + API + blog HTML

apps/accounts/
  models.py             Profile (1:1 User extension: bio, avatar, website)
  views.py              register, profile (edit), public_profile
  forms.py              RegisterForm, ProfileForm, UserForm
  signals.py            Auto-create Profile on User creation
  urls.py               Auth views (login/logout/register/profile/password-reset)

apps/blog/
  models.py             Category, Tag, Post (Article alias), Comment
  views.py              ArticleListView, ArticleDetailView, PostCreateView,
                        PostUpdateView, PostDeleteView, DashboardView
  forms.py              PostForm, CommentForm
  viewsets.py           DRF ViewSets: Category, Tag, Article, Comment
  serializers.py        DRF serializers with nested relations
  urls.py               HTML routes + DRF router (api_urlpatterns)
  management/commands/seed_data.py   Demo data seeder

templates/
  base/base.html        Bootstrap 5 layout with navbar, messages, footer
  accounts/             Login, register, profile, password reset templates
  blog/                 Article list, detail, post form, dashboard, delete confirm

static/css/style.css    Custom styles layered on Bootstrap 5
```

## URL Structure

### HTML Pages
| URL | View | Description |
|-----|------|-------------|
| `/` | ArticleListView | Published posts with search and filtering |
| `/tag/<slug>/` | ArticleListView | Filter by tag |
| `/category/<slug>/` | ArticleListView | Filter by category |
| `/articles/<slug>/` | ArticleDetailView | Post detail with comments |
| `/posts/new/` | PostCreateView | Create new post (login required) |
| `/posts/<slug>/edit/` | PostUpdateView | Edit post (author/staff only) |
| `/posts/<slug>/delete/` | PostDeleteView | Delete post (author/staff only) |
| `/dashboard/` | DashboardView | My posts / all posts for staff |
| `/accounts/login/` | LoginView | Django auth login |
| `/accounts/register/` | register | User registration |
| `/accounts/profile/` | profile | Edit own profile |
| `/accounts/profile/<username>/` | public_profile | Public user profile |
| `/admin/` | Django Admin | Full admin interface |

### REST API (`/api/`)
| Endpoint | Methods | Auth |
|----------|---------|------|
| `/api/articles/` | GET, POST | Read: public, Write: admin |
| `/api/articles/{id}/` | GET, PUT, DELETE | Read: public, Write: admin |
| `/api/articles/{id}/publish/` | POST | Admin |
| `/api/articles/{id}/archive/` | POST | Admin |
| `/api/articles/{id}/add-comment/` | POST | Authenticated |
| `/api/categories/` | GET, POST | Read: public, Write: admin |
| `/api/tags/` | GET, POST | Read: public, Write: admin |
| `/api/comments/` | GET, POST | Read: public, Write: authenticated |
| `/api/comments/{id}/approve/` | POST | Admin |

## Models

### Post (aliased as Article)
- `title`, `slug` (auto-generated, deduplicated), `content`, `excerpt`
- `author` (FK to User), `category` (FK, nullable), `tags` (M2M)
- `status`: draft / published / archived
- `featured_image`, `views` (auto-incremented), `published_at`, `created_at`, `updated_at`

### Comment
- `post` (FK), `author` (FK to User), `content`
- `approved` (default False -- must be approved before display)

### Category
- `name`, `slug` (auto-generated), `description`

### Tag
- `name`, `slug` (auto-generated)

### Profile (accounts)
- `user` (1:1 to auth.User), `bio`, `avatar` (ImageField), `website`, `created_at`

## Rules

- Always create migrations for model changes: `python manage.py makemigrations`
- Use class-based views for CRUD, function views for simple endpoints
- Parameterized queries only -- never raw SQL with string interpolation
- All new models need proper `__str__` and `Meta.ordering`
- Settings: use `os.environ.get()` with sensible defaults -- never crash on missing env vars
- Tests: use pytest + factory-boy, not Django TestCase
- Factory-boy: use `factory.Faker("text")` not `factory.Faker("paragraphs", as_text=True)` (removed in newer Faker)
- Template inheritance: extend `base/base.html`, use `{% block content %}` and `{% block title %}`
- Forms: use crispy-forms with `{{ form|crispy }}` for Bootstrap 5 styling
- Comments require approval (`approved=True`) before display on the public site
- Dashboard shows own posts for regular users, all posts for staff
- The `Article` name is an alias for `Post` for backward compatibility
