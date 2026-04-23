"""Management command to seed the database with demo data.

Creates 5 users, 5 categories, 10 tags, 10 published posts, and 15 comments.
Safe to run multiple times — skips if data already exists.

Usage:
    python manage.py seed_data
    python manage.py seed_data --flush   # Clear existing data first
"""
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.blog.models import Category, Comment, Post, Tag


CATEGORIES = [
    ("Python", "Articles about the Python programming language and ecosystem."),
    ("Django", "Tutorials, tips, and best practices for Django development."),
    ("JavaScript", "Frontend and backend JavaScript topics."),
    ("DevOps", "Deployment, CI/CD, Docker, and infrastructure."),
    ("Career", "Career advice, interviews, and professional development."),
]

TAGS = [
    "python", "django", "rest-api", "testing", "docker",
    "tutorial", "beginner", "advanced", "database", "deployment",
]

USERS = [
    ("alice", "alice@example.com", "Alice", "Johnson"),
    ("bob", "bob@example.com", "Bob", "Smith"),
    ("carol", "carol@example.com", "Carol", "Williams"),
    ("dave", "dave@example.com", "Dave", "Brown"),
    ("eve", "eve@example.com", "Eve", "Davis"),
]

POSTS = [
    {
        "title": "Getting Started with Django 5.2",
        "content": (
            "Django 5.2 is a powerful web framework that makes it easy to build "
            "web applications quickly. In this guide, we'll walk through setting up "
            "your first Django project from scratch.\n\n"
            "First, install Django using pip:\n\n"
            "    pip install Django>=5.2\n\n"
            "Then create a new project:\n\n"
            "    django-admin startproject mysite\n\n"
            "Django follows the model-view-template (MVT) pattern. Models define your "
            "data, views handle business logic, and templates render HTML. The framework "
            "includes an ORM, admin interface, authentication system, and much more out of the box.\n\n"
            "One of Django's greatest strengths is its 'batteries included' philosophy. "
            "You get URL routing, form handling, security middleware, and database migrations "
            "without installing any third-party packages."
        ),
        "excerpt": "A beginner-friendly guide to setting up your first Django 5.2 project.",
        "category": "Django",
        "tags": ["django", "tutorial", "beginner"],
        "author_idx": 0,
    },
    {
        "title": "Building REST APIs with Django REST Framework",
        "content": (
            "Django REST Framework (DRF) is the go-to library for building APIs in Django. "
            "It provides serializers, viewsets, authentication, and pagination out of the box.\n\n"
            "Start by installing DRF:\n\n"
            "    pip install djangorestframework\n\n"
            "Add 'rest_framework' to INSTALLED_APPS, then create a serializer for your model:\n\n"
            "Serializers convert Django model instances to JSON and back. ViewSets combine "
            "the logic for listing, creating, updating, and deleting resources into a single class.\n\n"
            "DRF also includes a browsable API — a web-based interface for testing your "
            "endpoints directly in the browser. This makes development and debugging much faster."
        ),
        "excerpt": "Learn how to build robust REST APIs using Django REST Framework.",
        "category": "Django",
        "tags": ["django", "rest-api", "tutorial"],
        "author_idx": 1,
    },
    {
        "title": "Python Testing Best Practices",
        "content": (
            "Writing tests is essential for maintaining code quality. Python has excellent "
            "testing tools including pytest, unittest, and coverage.py.\n\n"
            "Pytest is the most popular testing framework for Python. It offers simple syntax, "
            "powerful fixtures, and rich plugin ecosystem.\n\n"
            "Key principles for effective testing:\n\n"
            "1. Test behavior, not implementation\n"
            "2. Use factories instead of fixtures for test data\n"
            "3. Keep tests independent — no shared state\n"
            "4. Aim for 80%+ code coverage on new code\n"
            "5. Use mocking sparingly — prefer integration tests\n\n"
            "For Django projects, pytest-django provides fixtures like 'client', 'admin_client', "
            "and database access markers that simplify testing Django views and models."
        ),
        "excerpt": "Essential testing practices for Python developers using pytest.",
        "category": "Python",
        "tags": ["python", "testing", "tutorial"],
        "author_idx": 2,
    },
    {
        "title": "Docker for Django Developers",
        "content": (
            "Containerizing your Django application with Docker ensures consistent environments "
            "across development, testing, and production.\n\n"
            "A typical Dockerfile for Django:\n\n"
            "    FROM python:3.13-slim\n"
            "    WORKDIR /app\n"
            "    COPY requirements.txt .\n"
            "    RUN pip install -r requirements.txt\n"
            "    COPY . .\n"
            "    CMD [\"gunicorn\", \"config.wsgi:application\"]\n\n"
            "Use docker-compose to orchestrate your Django app with PostgreSQL and Redis. "
            "This setup lets new team members get running with a single command:\n\n"
            "    docker-compose up\n\n"
            "Tips for production Docker images: use multi-stage builds, run as non-root user, "
            "and pin your base image version."
        ),
        "excerpt": "How to containerize your Django app with Docker and docker-compose.",
        "category": "DevOps",
        "tags": ["docker", "django", "deployment"],
        "author_idx": 0,
    },
    {
        "title": "Understanding Python Decorators",
        "content": (
            "Decorators are one of Python's most powerful features. They let you modify "
            "or extend the behavior of functions and classes without changing their source code.\n\n"
            "A decorator is simply a function that takes another function as an argument "
            "and returns a new function. The @syntax is syntactic sugar for this pattern.\n\n"
            "Common use cases for decorators:\n\n"
            "- Logging and timing function calls\n"
            "- Authentication and permission checks\n"
            "- Caching and memoization\n"
            "- Input validation\n"
            "- Rate limiting\n\n"
            "Django uses decorators extensively: @login_required, @permission_required, "
            "@csrf_exempt, and @cached_property are all decorators you'll encounter regularly."
        ),
        "excerpt": "A deep dive into Python decorators and how to write your own.",
        "category": "Python",
        "tags": ["python", "advanced"],
        "author_idx": 3,
    },
    {
        "title": "Database Optimization in Django",
        "content": (
            "As your Django application grows, database queries can become a bottleneck. "
            "Understanding Django's ORM query behavior is crucial for performance.\n\n"
            "Key optimization techniques:\n\n"
            "1. Use select_related() for foreign key lookups\n"
            "2. Use prefetch_related() for many-to-many relationships\n"
            "3. Use only() and defer() to limit fetched columns\n"
            "4. Add database indexes for frequently queried fields\n"
            "5. Use django-debug-toolbar to identify N+1 queries\n\n"
            "The Django Debug Toolbar is an invaluable tool during development. "
            "It shows every SQL query executed for a page load, making it easy to spot "
            "inefficient query patterns."
        ),
        "excerpt": "Tips for optimizing database performance in Django applications.",
        "category": "Django",
        "tags": ["django", "database", "advanced"],
        "author_idx": 1,
    },
    {
        "title": "Modern JavaScript for Backend Developers",
        "content": (
            "Even if you primarily work on the backend, understanding modern JavaScript "
            "is essential for full-stack development.\n\n"
            "Key ES6+ features every developer should know:\n\n"
            "- Arrow functions and template literals\n"
            "- Destructuring and spread operator\n"
            "- Promises, async/await\n"
            "- Modules (import/export)\n"
            "- Map, Set, and other built-in data structures\n\n"
            "For Django developers, JavaScript is useful for adding interactivity to templates, "
            "building API-driven frontends, and working with tools like htmx or Alpine.js "
            "that pair naturally with server-rendered HTML."
        ),
        "excerpt": "Essential JavaScript concepts for Python/Django developers.",
        "category": "JavaScript",
        "tags": ["beginner", "tutorial"],
        "author_idx": 4,
    },
    {
        "title": "CI/CD Pipelines with GitHub Actions",
        "content": (
            "Automating your test and deployment workflow with GitHub Actions saves time "
            "and reduces errors.\n\n"
            "A typical Django CI pipeline:\n\n"
            "1. Install Python and dependencies\n"
            "2. Run linting (ruff check)\n"
            "3. Run type checking (mypy)\n"
            "4. Run tests with coverage\n"
            "5. Build Docker image\n"
            "6. Deploy to staging/production\n\n"
            "GitHub Actions uses YAML workflow files in .github/workflows/. Each workflow "
            "consists of triggers, jobs, and steps. You can reuse community actions from "
            "the GitHub Marketplace or write custom scripts."
        ),
        "excerpt": "Set up automated testing and deployment for Django with GitHub Actions.",
        "category": "DevOps",
        "tags": ["deployment", "testing", "docker"],
        "author_idx": 2,
    },
    {
        "title": "Landing Your First Developer Job",
        "content": (
            "Breaking into software development can feel overwhelming, but with the right "
            "approach it's achievable.\n\n"
            "Steps to prepare:\n\n"
            "1. Build real projects, not just tutorials\n"
            "2. Contribute to open source\n"
            "3. Write about what you learn (start a blog!)\n"
            "4. Practice coding challenges\n"
            "5. Network at meetups and online communities\n\n"
            "During interviews, companies are looking for:\n"
            "- Problem-solving ability over memorized algorithms\n"
            "- Communication skills and willingness to learn\n"
            "- Understanding of fundamentals (HTTP, databases, version control)\n"
            "- Ability to write clean, tested code\n\n"
            "Don't wait until you feel 'ready' — apply early and often. "
            "Many successful developers started with less experience than you might think."
        ),
        "excerpt": "Practical advice for aspiring developers looking for their first role.",
        "category": "Career",
        "tags": ["beginner"],
        "author_idx": 3,
    },
    {
        "title": "Django Security Checklist",
        "content": (
            "Security is a critical aspect of web development. Django provides many security "
            "features out of the box, but you need to configure them correctly.\n\n"
            "Essential security settings for production:\n\n"
            "- Set SECRET_KEY from environment variable (never hardcode)\n"
            "- Set DEBUG = False\n"
            "- Configure ALLOWED_HOSTS\n"
            "- Enable SECURE_SSL_REDIRECT, SECURE_HSTS_SECONDS\n"
            "- Set SESSION_COOKIE_SECURE and CSRF_COOKIE_SECURE\n"
            "- Use parameterized queries (never raw SQL with string formatting)\n"
            "- Validate and sanitize all user input\n"
            "- Keep dependencies updated\n\n"
            "Django's built-in protections include CSRF tokens, XSS prevention via template "
            "auto-escaping, clickjacking protection, and SQL injection prevention through the ORM."
        ),
        "excerpt": "A comprehensive security checklist for Django production deployments.",
        "category": "Django",
        "tags": ["django", "deployment", "advanced"],
        "author_idx": 4,
    },
]

COMMENTS = [
    (0, 1, "Great introduction! This helped me get started with Django quickly."),
    (0, 2, "Very clear explanation. Would love to see a follow-up on Django templates."),
    (1, 0, "DRF is amazing. The browsable API alone is worth installing it."),
    (1, 3, "Can you cover token authentication in a future post?"),
    (2, 4, "pytest is so much better than unittest. Great tips here."),
    (2, 0, "The factory_boy recommendation is spot on. Changed how I write tests."),
    (3, 1, "Docker + Django is a game changer for team onboarding."),
    (4, 2, "Finally understand decorators! The Django examples really helped."),
    (4, 4, "Could you write about context managers next? Similar concept."),
    (5, 3, "select_related saved us from hundreds of extra queries. Essential knowledge."),
    (5, 0, "Django Debug Toolbar is a must-have. Great recommendation."),
    (6, 1, "As a Django developer learning JS, this was exactly what I needed."),
    (7, 4, "Our team uses GitHub Actions for everything now. Solid guide."),
    (8, 2, "Encouraging post. I landed my first job 3 months after following similar advice."),
    (9, 3, "This should be required reading for every Django developer going to production."),
]


class Command(BaseCommand):
    help = "Seed the database with demo data (5 users, 10 posts, 15 comments, 5 categories)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete existing blog data before seeding.",
        )

    def handle(self, *args, **options):
        if options["flush"]:
            self.stdout.write("Flushing existing blog data...")
            Comment.objects.all().delete()
            Post.objects.all().delete()
            Tag.objects.all().delete()
            Category.objects.all().delete()
            User.objects.filter(username__in=[u[0] for u in USERS]).delete()

        # Check if data already exists
        if Post.objects.exists() and not options["flush"]:
            self.stdout.write(self.style.WARNING("Data already exists. Use --flush to reset."))
            return

        # Create users
        users = []
        for username, email, first_name, last_name in USERS:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                },
            )
            if created:
                user.set_password("demo1234")
                user.save()
            users.append(user)
        self.stdout.write(f"  Created {len(users)} users (password: demo1234)")

        # Create superuser if none exists
        if not User.objects.filter(is_superuser=True).exists():
            admin = User.objects.create_superuser(
                username="admin",
                email="admin@example.com",
                password="admin1234",
                first_name="Admin",
                last_name="User",
            )
            self.stdout.write(f"  Created superuser: admin / admin1234")

        # Create categories
        categories = {}
        for name, description in CATEGORIES:
            cat, _ = Category.objects.get_or_create(name=name, defaults={"description": description})
            categories[name] = cat
        self.stdout.write(f"  Created {len(categories)} categories")

        # Create tags
        tags = {}
        for tag_name in TAGS:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            tags[tag_name] = tag
        self.stdout.write(f"  Created {len(tags)} tags")

        # Create posts
        now = timezone.now()
        posts = []
        for i, post_data in enumerate(POSTS):
            post = Post.objects.create(
                title=post_data["title"],
                content=post_data["content"],
                excerpt=post_data["excerpt"],
                author=users[post_data["author_idx"]],
                category=categories[post_data["category"]],
                status=Post.STATUS_PUBLISHED,
                published_at=now - timezone.timedelta(days=len(POSTS) - i),
            )
            for tag_name in post_data["tags"]:
                post.tags.add(tags[tag_name])
            posts.append(post)
        self.stdout.write(f"  Created {len(posts)} posts")

        # Create comments (all approved for demo)
        comment_count = 0
        for post_idx, author_idx, content in COMMENTS:
            Comment.objects.create(
                post=posts[post_idx],
                author=users[author_idx],
                content=content,
                approved=True,
            )
            comment_count += 1
        self.stdout.write(f"  Created {comment_count} comments")

        self.stdout.write(self.style.SUCCESS("\nDemo data seeded successfully!"))
        self.stdout.write("  Login credentials:")
        self.stdout.write("    Admin: admin / admin1234")
        self.stdout.write("    Users: alice, bob, carol, dave, eve / demo1234")
