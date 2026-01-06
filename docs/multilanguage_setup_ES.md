## 💡 1. Configura los idiomas en `config/settings.py`

```python
from pathlib import Path
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent

LANGUAGE_CODE = 'en'

LANGUAGES = [
    ('en', _('English')),
    ('es', _('Español')),
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

## 🔊 2. Marca los textos traducibles

### En vistas:

```python
from django.utils.translation import gettext as _
from django.http import HttpResponse

def index(request):
    return HttpResponse(_("Welcome to the polls app!"))
```

### En plantillas:

```html
{% load i18n %}
<h1>{% trans "Welcome to the polls app!" %}</h1>
```

---

## 🔧 3. Genera los archivos de traducción

Ejecuta desde la raíz del proyecto:

```bash
python manage.py makemessages -l es
```

Esto creará:

```
locale/
└── es/
    └── LC_MESSAGES/
        └── django.po
```

---

## 🖊️ 4. Edita el archivo `django.po`

Abre `locale/es/LC_MESSAGES/django.po` y agrega tus traducciones:

```po
msgid "Welcome to the polls app!"
msgstr "¡Bienvenido a la aplicación de encuestas!"
```

---

## ⚙️ 5. Compila las traducciones

```bash
python manage.py compilemessages
```

Esto genera los archivos `.mo` binarios necesarios.

---

## 🌐 6. Habilita el selector de idioma

En `settings.py`, agrega el middleware:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # <--- Importante
    'django.middleware.common.CommonMiddleware',
    ...
]
```

Y en `config/urls.py`:

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

## 🛈 7. Cambiar idioma desde el navegador

```html
<form action="/i18n/setlang/" method="post">
  {% csrf_token %}
  <select name="language">
    <option value="en">English</option>
    <option value="es">Español</option>
  </select>
  <button type="submit">Cambiar idioma</button>
</form>
```

---

## ✅ Resultado

* Soporte para múltiples idiomas en todo el proyecto.
* Traducciones gestionadas mediante archivos `.po` y `.mo`.
* Middleware `LocaleMiddleware` activado.