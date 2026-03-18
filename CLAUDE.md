# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Django 6.0.3 web application using Python 3.13.5 with SQLite3. It is in early development — no custom apps exist yet beyond the default Django admin setup.

## Commands

Activate the virtual environment before running any commands:

```bash
source venv/Scripts/activate  # Windows (Git Bash)
# or
venv\Scripts\activate.bat     # Windows CMD
```

Common management commands:

```bash
python manage.py runserver          # Start development server
python manage.py migrate            # Apply migrations
python manage.py makemigrations     # Generate migrations from model changes
python manage.py createsuperuser    # Create admin user
python manage.py test               # Run tests
python manage.py test <app>.tests.TestClass.test_method  # Run a single test
```

## Architecture

- `DICAS_PROJECT/settings.py` — Django settings (DEBUG=True, SQLite, UTC)
- `DICAS_PROJECT/urls.py` — URL routing (currently only `/admin/`)
- `DICAS_PROJECT/wsgi.py` / `asgi.py` — WSGI/ASGI entry points

New Django apps should be created with `python manage.py startapp <name>` and registered in `INSTALLED_APPS` in `settings.py`. App URLs should be included in `DICAS_PROJECT/urls.py` via `include()`.

When adding packages, update `requirements.txt` with `pip freeze > requirements.txt`.
