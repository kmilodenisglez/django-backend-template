## 🧩 Custom Command: `startapp_in_apps`

This project includes a **custom Django management command** designed to create new applications directly inside the `apps/` directory, instead of Django’s default behavior which creates them at the project root.

### 🚀 Usage

```bash
python manage.py startapp_in_apps <app_name>
```

For example:

```bash
python manage.py startapp_in_apps polls_d
```

This will automatically create the following structure:

```
isowo/
├── apps/
│   └── polls_d/
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── migrations/
│       ├── models.py
│       ├── tests.py
│       └── views.py
```

### 🧠 Description

The `startapp_in_apps` command extends Django’s built-in `startapp` command.
Its purpose is to maintain a **modular and organized architecture** by grouping all internal applications under the main `apps/` directory.

### ⚙️ Command Location

The implementation of the command can be found at:

```
config/management/commands/startapp_in_apps.py
```

### 🧩 Registering the App

After creating a new app, register it in your `config/settings.py` file under `INSTALLED_APPS`.

You can do this in two valid ways:

#### Option 1 — Short form (recommended)

```python
INSTALLED_APPS = [
    'apps.polls_d',
]
```

#### Option 2 — Explicit form

```python
INSTALLED_APPS = [
    'apps.polls_d.apps.PollsDConfig',
]
```

> 💡 The short form is perfectly fine unless your `AppConfig` class contains custom initialization logic.
