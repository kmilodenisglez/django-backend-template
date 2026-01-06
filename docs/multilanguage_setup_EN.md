## 💡 1. Configure languages in `config/settings.py`

```python
from pathlib import Path
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent

LANGUAGE_CODE = 'en'

LANGUAGES = [
    ('en', _('English')),
    ('es', _('Spanish')),
]

TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]
```

---

## 🔊 2. Mark translatable strings

### In views:

```python
from django.utils.translation import gettext as _
from django.http import HttpResponse

def index(request):
    return HttpResponse(_("Welcome to the polls app!"))
```

### In templates:

```html
{% load i18n %}
<h1>{% trans "Welcome to the polls app!" %}</h1>
```

---

## 🔧 3. Generate translation files

Run from the project root:

```bash
python manage.py makemessages -l es
```

This creates:

```
locale/
└── es/
    └── LC_MESSAGES/
        └── django.po
```

---

## 🖊️ 4. Edit the `django.po` file

Open `locale/es/LC_MESSAGES/django.po` and add your translations:

```po
msgid "Welcome to the polls app!"
msgstr "¡Bienvenido a la aplicación de encuestas!"
```

---

## ⚙️ 5. Compile translations

```bash
python manage.py compilemessages
```

This generates the binary `.mo` files Django uses.

---

## 🌐 6. Enable language switching

In `settings.py`, add the middleware:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # <--- Important
    'django.middleware.common.CommonMiddleware',
    ...
]
```

And in `config/urls.py`:

```python
from django.conf.urls.i18n import i18n_patterns
from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('polls/', include('apps.polls.urls')),
)
```

---

## 🛈 7. Change language from browser

```html
<form action="/i18n/setlang/" method="post">
  {% csrf_token %}
  <select name="language">
    <option value="en">English</option>
    <option value="es">Español</option>
  </select>
  <button type="submit">Change language</button>
</form>
```

---

## ✅ Result

* Multi-language support across the entire project.
* Translations managed via `.po` and `.mo` files.
* `LocaleMiddleware` activated for dynamic language switching.
