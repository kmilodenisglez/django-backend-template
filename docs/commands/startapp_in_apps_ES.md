## 🧩 Comando personalizado: `startapp_in_apps`

Este proyecto incluye un **comando de gestión personalizado** para crear nuevas aplicaciones dentro del directorio `apps/`, en lugar del comportamiento por defecto de Django que las crea en la raíz del proyecto.

### 🚀 Uso

```bash
python manage.py startapp_in_apps <nombre_app>
```

Por ejemplo:

```bash
python manage.py startapp_in_apps polls_d
```

Esto creará automáticamente la siguiente estructura:

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

### 🧠 Descripción

El comando `startapp_in_apps` es una extensión del comando nativo `startapp` de Django.
Su objetivo es mantener una arquitectura modular y limpia, agrupando todas las aplicaciones dentro del directorio `apps/` del proyecto.

### ⚙️ Ubicación del comando

El comando se encuentra implementado en:

```
config/management/commands/startapp_in_apps.py
```

### 🧩 Registro de la aplicación

Una vez creada la app, debes registrarla en `config/settings.py`, dentro de la lista `INSTALLED_APPS`.

Puedes hacerlo de dos formas válidas:

#### Opción 1 — Forma corta (recomendada)

```python
INSTALLED_APPS = [
    'apps.polls_d',
]
```

#### Opción 2 — Forma explícita

```python
INSTALLED_APPS = [
    'apps.polls_d.apps.PollsDConfig',
]
```

> 💡 La forma corta es suficiente si no tienes lógica personalizada en el `AppConfig`.
