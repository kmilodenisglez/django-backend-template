# Django Backend Template

A batteries-included Django backend template focused on building maintainable REST APIs and subscription-based services. This repository provides a clean project layout, helpful management commands, i18n support, test scaffolding, and best-practice tooling to jumpstart new projects.

## Features

- Role-based access control (RBAC)
- Subscription/payment integration scaffolding
- Internationalization (`locale/` includes Spanish)
- Pytest test setup and example tests
- Poetry-managed dependencies and `pyproject.toml`
- Pre-commit hooks and Ruff for linting/formatting

## Quick start

1. Clone the repo:

```bash
git clone https://github.com/kmilodenisglez/django-backend-template.git
cd django-backend-template
```

2. Install dependencies (Poetry recommended):

```bash
poetry install
```

3. Copy the example env and edit as needed:

```bash
cp .env.example .env
# edit .env and set DJANGO_SECRET_KEY and database/email settings
```

4. Apply migrations and create a superuser:

```bash
python manage.py migrate
python manage.py createsuperuser
```

5. Run the development server:

```bash
python manage.py runserver
```

## Using this repository as a GitHub template

- On GitHub, click the **Use this template** button (top-right) to create a new repository pre-populated with this code.
- Or create a new repo locally from this template and push to your own remote:

```bash
# create a new repository on GitHub, then:
git remote remove origin
git remote add origin https://github.com/<your-user>/<your-repo>.git
git push -u origin main
```

## Project structure (high level)

```
/apps/            # all Django apps live here
config/           # Django settings & URL conf
manage.py
pyproject.toml
locale/            # translation files
docs/              # additional documentation and commands
README.md
```

## Developer notes

- Use `python manage.py startapp_in_apps <name>` to create apps inside `apps/`.
- Tests: run `pytest` (project is configured for pytest-django).
- Formatting: `ruff format .` and `ruff check .`.
- Install git hooks: `pre-commit install`.

## Contributing

- Follow the contributing guidelines in `docs/CONTRIBUTING.md` and use the included Makefile targets for common tasks.

## License

This project is provided under the Apache 2.0 license — see `LICENSE`.

## Contact

- Author: kmilo
# Isowo

[![CI](https://github.com/owo-nla/isowo/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/owo-nla/isowo/actions/workflows/ci.yml?branch=main)

<!-- Replace OWNER/REPO in the badge URL with your GitHub repo to show workflow status -->

**Isowo** is a full-featured classified ads platform built with Django 5.2. It provides a modular architecture with all internal apps organized inside the `apps/` directory, making it easy to maintain and extend.

---

## 🎯 Project Overview

Isowo is a classified advertisements platform that allows users to:

- Create, edit, and manage classified ads
- Upload multiple images per ad (up to 10)
- Organize ads by categories
- Search and filter ads
- Favorite/bookmark ads
- Manage user profiles
- Set ad expiration dates
- Receive email notifications

---

## ✨ Key Features

### 📝 Ad Management

- **CRUD Operations**: Create, read, update, and delete ads
- **Multiple Images**: Upload up to 10 images per ad with drag-and-drop reordering
- **Image Management**: Delete and reorder images when editing ads
- **Categories**: Organize ads by categories
- **Search**: Full-text search across titles and descriptions
- **Expiration**: Set expiration dates for ads with automatic deactivation

### 👤 User Features

- **Authentication**: Email/username login with social authentication (Facebook, Google)
- **User Profiles**: Extended profiles with bio, location, phone, avatar, and website
- **Favorites**: Bookmark favorite ads for easy access
- **Email Notifications**: Receive emails when ads are created or favorited

### 💳 Subscription System
- **Plans**: Monthly and Annual subscription plans
- **Discounts**: Automatic discounts for longer durations
- **Multi-Payment**: Support for Credit Card (Stripe) and Crypto (USDT via NowPayments)
- **Management**: User dashboard to view subscription status

### 📍 Geographic Location System
- **Hierarchical Geo Data**: Country → Province → Municipality three-tier organization
- **Flexible Coverage Zones**: Multi-region coverage for ads serving multiple provinces/municipalities
- **Location-Based Search**: Search and filter ads by geographic location
- **REST API**: Complete DRF endpoints for geo data and location-based filtering
- **Sample Data**: Pre-loaded Cuba geographic data with 16 provinces and 166 municipalities

### 🛡 Role-Based Access Control (RBAC)
- **Moderator Role**: Dedicated role for content moderation
- **Permissions**: Granular control over ad editing and category management
- **Admin Tools**: Enhanced admin interface for moderators

### 🌍 Internationalization

- Multi-language support (English, Spanish)
- Language switching in UI
- Translation files in `locale/` folder

### 🛠 Developer Features

- **Modular Architecture**: All apps in `apps/` directory
- **Custom Commands**: `startapp_in_apps` for creating new apps
- **Code Quality**: Ruff for linting and formatting
- **Testing**: pytest and pytest-django configured

---

## 🛠 Technology Stack

- **Framework**: Django 5.2.7
- **Python**: >=3.13
- **Database**: SQLite (development), ready for PostgreSQL
- **Authentication**: django-allauth
- **Image Processing**: Pillow
- **Code Quality**: Ruff, pre-commit hooks
- **Testing**: pytest, pytest-django
- **Production**: Gunicorn

---

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- Poetry (recommended) or pip/venv

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd isowo

# Install dependencies
poetry install
# or: pip install -r requirements.txt

# Create environment file (optional)
cp .env.example .env  # Edit with your settings

# Apply migrations
python manage.py migrate

# Setup RBAC roles
python manage.py setup_roles

# Initialize Payment Methods
python manage.py init_payment_methods

# Create superuser (optional)
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

Visit `http://localhost:8000` to see the application.

---

## 🧑‍💻 Developer setup (recommended)

If you're contributing or working on the codebase, follow these steps to set up a consistent development environment and automatic formatting checks.

1. Install development dependencies (Poetry recommended):

```bash
# Install pinned dev dependencies (includes ruff, pre-commit, pytest)
poetry install --no-interaction --no-ansi
# Or use your preferred virtualenv and pip
```

2. Bootstrap and install pre-commit hooks (Makefile shortcuts provided):

```bash
make bootstrap           # runs `poetry install` if Poetry is available
make install-pre-commit # installs pre-commit hooks
```

3. Run hooks across the repository (optional but recommended before large PRs):

```bash
make precommit-all
```

4. Formatting and linting

```bash
make format   # run ruff format
make lint     # run ruff check
make fix      # run ruff check --fix
```

5. Run tests

```bash
make test
# or
poetry run pytest -q
```

These steps use the included `Makefile` and will automatically use `poetry run` when Poetry is available. See `Makefile` and `.pre-commit-config.yaml` for details.

See the full contributing guide for developer workflow, PR checklist and coding standards:

 docs/CONTRIBUTING.md

## 📂 Project Structure

```tree
isowo/
├── apps/
│   ├── classifieds/       ← Main classifieds app
│   │   ├── models.py      ← Ad, Category, AdImage, Favorite, Country, Province, Municipality, CoverageZone, AdCoverage
│   │   ├── views.py       ← All view logic + geo API endpoints
│   │   ├── forms.py       ← Form definitions with cascading geo selectors
│   │   ├── serializers.py ← DRF serializers for API responses
│   │   ├── urls.py        ← URL routing
│   │   ├── admin.py       ← Admin configuration + geo model admins
│   │   ├── utils.py       ← Email notifications + location filtering
│   │   ├── signals.py     ← Auto-create user profiles
│   │   ├── management/
│   │   │   └── commands/
│   │   │       ├── deactivate_expired_ads.py
│   │   │       └── populate_geo_data.py
│   │   ├── static/
│   │   │   └── classifieds/js/
│   │   │       └── geo_cascade.js ← Client-side geo filtering
│   │   └── migrations/
│   └── core/             ← Shared utilities and custom commands
├── config/                 ← Project configuration
│   ├── settings.py         ← Django settings
│   ├── urls.py             ← Root URL configuration + DRF router
│   ├── wsgi.py
│   └── asgi.py
├── templates/              ← HTML templates
│   └── classifieds/
├── static/                 ← Static files (CSS, JS, images)
├── media/                  ← User-uploaded files
├── locale/                 ← Translation files
├── docs/                   ← Documentation
├── manage.py
├── pyproject.toml          ← Poetry dependencies
└── README.md

```

---

## 🧩 Custom Django Commands

### `startapp_in_apps`

Creates new Django apps inside the `apps/` folder:

```bash
python manage.py startapp_in_apps <app_name>
```

This automatically:

- Creates the app in `apps/<app_name>/`
- Adds it to `INSTALLED_APPS` in `settings.py`

📚 [Full Documentation](docs/commands/startapp_in_apps_EN.md)

### `deactivate_expired_ads`

Deactivates ads that have passed their expiration date:

```bash
python manage.py deactivate_expired_ads
```

**Recommended**: Schedule this command to run periodically (cron, task scheduler).

### `populate_geo_data`

Populates geographic reference data (countries, provinces, municipalities):

```bash
# Create sample data for Cuba with 16 provinces and 166 municipalities
python manage.py populate_geo_data --create-sample

# Load data from JSON fixture file
python manage.py populate_geo_data --fixture path/to/fixture.json

# Clear all existing geographic data before loading new data
python manage.py populate_geo_data --clear --create-sample
```

**Sample Data**: Includes complete Cuban geographic hierarchy (Artemisa, Camagüey, Ciego de Ávila, Cienfuegos, Granma, Guantánamo, Holguín, La Habana, Las Tunas, Matanzas, Mayabeque, Pinar del Río, Sancti Spíritus, Santiago de Cuba, Villa Clara, Isla de la Juventud).

📚 [Full Geographic Setup Guide](docs/GEO_SETUP.md)

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
DEBUG=True
# The project uses `django_settings_env` which prefixes env vars with `DJANGO_`.
# Provide the secret as `DJANGO_SECRET_KEY`; it will populate `SECRET_KEY`.
DJANGO_SECRET_KEY=your-secret-key-here
DEFAULT_FROM_EMAIL=noreply@isowo.com
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-password
```

### Email Settings

By default, emails are sent to the console (development). For production:

- Update `EMAIL_*` settings in `.env` or `settings.py`
- Or configure SMTP settings

### Social Authentication

Configure social providers in Django admin:

1. Go to `/admin/sites/site/` and set your site domain
2. Go to `/admin/socialaccount/socialapp/` and add Facebook/Google apps
3. Update credentials in `settings.py` or `.env`

---

## 🌍 Multilanguage Support

The project supports multiple languages using Django's i18n system:

- **Languages**: English (default), Spanish
- **Translation files**: `locale/` folder
- **Language switching**: Available in UI

📘 [Setup Guide](docs/multilanguage_setup_EN.md)

---

## 📝 Important Notes

- **Database**: Uses SQLite for development. For production, switch to PostgreSQL
- **Static Files**: Run `python manage.py collectstatic` before deployment
- **Media Files**: Configure proper storage (S3, CDN) for production
- **Security**: Set `DEBUG=False` and configure `ALLOWED_HOSTS` for production
- **Migrations**: Always create migrations after model changes: `python manage.py makemigrations`

---

## 🛡 Moderation & Admin

- **Moderator capabilities**: Users in the `Moderator` group (or staff/superusers) can manage listings from the Django admin: change category, modify fields, or delete listings that violate platform policies.
- **Owner notifications**: When a moderator changes a listing's category or deletes a listing, the system will attempt to notify the listing owner by email (only for registered users with a configured email).
- **Admin action**: There's an admin action `Notify owner(s) about moderation action` available on the `Ad` admin list to send generic moderation notices to selected owners.

## ☁ CI and Tests

- The project CI workflow was consolidated into a single matrix job (`.github/workflows/ci.yml`) that runs tests across supported Python versions.
- Preferred local test runner: `pytest` (configured with `pytest-django`). When running the tests with Django runtime settings explicitly set, use:

```bash
# recommended: run tests with the Django settings module set
DJANGO_SETTINGS_MODULE=config.settings poetry run pytest -q
```


## 🧪 Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
ruff check .
ruff format .
```

### Pre-commit Hooks

```bash
pre-commit install
```

---

## 📚 Documentation

- [Custom Commands](docs/commands/)
- [Geographic Setup & Location-Based Search](docs/GEO_SETUP.md)
- [Multilanguage Setup](docs/multilanguage_setup_EN.md)
- [Spanish README](README_ES.md)

---

## 🤝 Contributing

1. Create new apps using `startapp_in_apps` command
2. Follow Django best practices
3. Write tests for new features
4. Keep the `apps/` directory clean and modular

---

## 📄 License

Apache License 2.0 - See [LICENSE](LICENSE) file for details.

---

## 👤 Authors

**kmilo** - <kmilo.denis.glez@yandex.com>
