# Isowo

**Isowo** es una plataforma completa de anuncios clasificados construida con Django 5.2. Proporciona una arquitectura modular con todas las aplicaciones internas organizadas dentro del directorio `apps/`, facilitando el mantenimiento y la extensión.

---

## 🎯 Resumen del Proyecto

Isowo es una plataforma de anuncios clasificados que permite a los usuarios:

- Crear, editar y gestionar anuncios clasificados
- Subir múltiples imágenes por anuncio (hasta 10)
- Organizar anuncios por categorías
- Buscar y filtrar anuncios
- Marcar anuncios como favoritos
- Gestionar perfiles de usuario
- Establecer fechas de expiración para anuncios
- Recibir notificaciones por correo electrónico

---

## ✨ Características Principales

### 📝 Gestión de Anuncios

- **Operaciones CRUD**: Crear, leer, actualizar y eliminar anuncios
- **Múltiples Imágenes**: Subir hasta 10 imágenes por anuncio con reordenamiento por arrastre
- **Gestión de Imágenes**: Eliminar y reordenar imágenes al editar anuncios
- **Categorías**: Organizar anuncios por categorías
- **Búsqueda**: Búsqueda de texto completo en títulos y descripciones
- **Expiración**: Establecer fechas de expiración con desactivación automática

### 👤 Funciones de Usuario

- **Autenticación**: Inicio de sesión con email/usuario y autenticación social (Facebook, Google)
- **Perfiles de Usuario**: Perfiles extendidos con biografía, ubicación, teléfono, avatar y sitio web
- **Favoritos**: Marcar anuncios favoritos para acceso rápido
- **Notificaciones por Email**: Recibir correos cuando se crean o marcan como favoritos anuncios

### 💳 Sistema de Suscripciones
- **Planes**: Planes de suscripción mensuales y anuales
- **Descuentos**: Descuentos automáticos para duraciones más largas
- **Multi-Pago**: Soporte para Tarjeta de Crédito (Stripe) y Cripto (USDT vía NowPayments)
- **Gestión**: Panel de usuario para ver el estado de la suscripción

### 📍 Sistema de Ubicación Geográfica
- **Datos Geográficos Jerárquicos**: Organización de tres niveles País → Provincia → Municipio
- **Zonas de Cobertura Flexible**: Cobertura multi-región para anuncios que sirven múltiples provincias/municipios
- **Búsqueda por Ubicación**: Buscar y filtrar anuncios por ubicación geográfica
- **REST API**: Endpoints DRF completos para datos geo y filtrado basado en ubicación
- **Datos de Ejemplo**: Datos geográficos preestablecidos de Cuba con 16 provincias y 166 municipios

### 🛡 Control de Acceso Basado en Roles (RBAC)
- **Rol de Moderador**: Rol dedicado para la moderación de contenido
- **Permisos**: Control granular sobre la edición de anuncios y gestión de categorías
- **Herramientas de Admin**: Interfaz de administración mejorada para moderadores

### 🌍 Internacionalización

- Soporte multiidioma (Inglés, Español)
- Cambio de idioma en la interfaz
- Archivos de traducción en la carpeta `locale/`

### 🛠 Funciones para Desarrolladores

- **Arquitectura Modular**: Todas las apps en el directorio `apps/`
- **Comandos Personalizados**: `startapp_in_apps` para crear nuevas apps
- **Calidad de Código**: Ruff para linting y formateo
- **Pruebas**: pytest y pytest-django configurados

---

## 🛠 Stack Tecnológico

- **Framework**: Django 5.2.7
- **Python**: >=3.13
- **Base de Datos**: SQLite (desarrollo), listo para PostgreSQL
- **Autenticación**: django-allauth
- **Procesamiento de Imágenes**: Pillow
- **Calidad de Código**: Ruff, pre-commit hooks
- **Pruebas**: pytest, pytest-django
- **Producción**: Gunicorn

---

## 🚀 Inicio Rápido

### Prerrequisitos

- Python 3.13+
- Poetry (recomendado) o pip/venv

### Instalación

```bash
# Clonar el repositorio
git clone <url-del-repositorio>
cd isowo

# Instalar dependencias
poetry install
# o: pip install -r requirements.txt

# Crear archivo de entorno (opcional)
cp .env.example .env  # Editar con tus configuraciones

# Aplicar migraciones
python manage.py migrate

# Configurar roles RBAC
python manage.py setup_roles

# Inicializar Métodos de Pago
python manage.py init_payment_methods

# Crear superusuario (opcional)
python manage.py createsuperuser

# Ejecutar servidor de desarrollo
python manage.py runserver
```

Visita `http://localhost:8000` para ver la aplicación.

---

## 🧑‍💻 Configuración para desarrolladores (recomendado)

Si vas a contribuir o trabajar en la base de código, sigue estos pasos para configurar un entorno de desarrollo coherente y comprobaciones automáticas de formato:

1. Instala las dependencias de desarrollo (se recomienda Poetry):

```bash
# Instala dependencias de desarrollo (incluye ruff, pre-commit, pytest)
poetry install --no-interaction --no-ansi
# O usa tu virtualenv y pip preferido
```

2. Inicializa y instala los *pre-commit* (atajos con Makefile):

```bash
make bootstrap           # ejecuta `poetry install` si Poetry está disponible
make install-pre-commit # instala los hooks de pre-commit
```

3. Ejecuta los hooks en todo el repositorio (opcional pero recomendado antes de PRs grandes):

```bash
make precommit-all
```

4. Formateo y linting

```bash
make format   # ruff format
make lint     # ruff check
make fix      # ruff check --fix
```

5. Ejecuta las pruebas

```bash
make test
# o
poetry run pytest -q
```

Estos pasos usan el `Makefile` incluido y usarán `poetry run` cuando Poetry esté disponible. Consulta `Makefile` y `.pre-commit-config.yaml` para más detalles.

Consulta la guía completa de contribución para el flujo de trabajo del desarrollador, la lista de comprobación de PR y las normas de codificación:

 docs/CONTRIBUTING.md

## 📂 Estructura del Proyecto

```
isowo/
├── apps/
│   ├── classifieds/       ← App principal de clasificados
│   │   ├── models.py      ← Ad, Category, AdImage, Favorite, Country, Province, Municipality, CoverageZone, AdCoverage
│   │   ├── views.py       ← Toda la lógica de vistas + endpoints de API geo
│   │   ├── forms.py       ← Definiciones de formularios con selectores geo en cascada
│   │   ├── serializers.py ← Serializadores DRF para respuestas de API
│   │   ├── urls.py        ← Enrutamiento de URLs
│   │   ├── admin.py       ← Configuración de admin + admins de modelos geo
│   │   ├── utils.py       ← Notificaciones por email + filtrado de ubicación
│   │   ├── signals.py     ← Auto-crear perfiles de usuario
│   │   ├── management/
│   │   │   └── commands/
│   │   │       ├── deactivate_expired_ads.py
│   │   │       └── populate_geo_data.py
│   │   ├── static/
│   │   │   └── classifieds/js/
│   │   │       └── geo_cascade.js ← Filtrado geo del lado del cliente
│   │   └── migrations/
│   └── core/             ← Utilidades compartidas y comandos personalizados
├── config/                 ← Configuración del proyecto
│   ├── settings.py         ← Configuración de Django
│   ├── urls.py             ← Configuración de URLs raíz + router DRF
│   ├── wsgi.py
│   └── asgi.py
├── templates/              ← Plantillas HTML
│   └── classifieds/
├── static/                 ← Archivos estáticos (CSS, JS, imágenes)
├── media/                  ← Archivos subidos por usuarios
├── locale/                 ← Archivos de traducción
├── docs/                   ← Documentación
├── manage.py
├── pyproject.toml          ← Dependencias de Poetry
└── README.md
```

---

## 🧩 Comandos Personalizados de Django

### `startapp_in_apps`

Crea nuevas apps de Django dentro de la carpeta `apps/`:

```bash
python manage.py startapp_in_apps <nombre_app>
```

Esto automáticamente:

- Crea la app en `apps/<nombre_app>/`
- La agrega a `INSTALLED_APPS` en `settings.py`

📚 [Documentación Completa](docs/commands/startapp_in_apps_ES.md)

### `deactivate_expired_ads`

Desactiva anuncios que han pasado su fecha de expiración:

```bash
python manage.py deactivate_expired_ads
```

**Recomendado**: Programar este comando para ejecutarse periódicamente (cron, programador de tareas).

### `populate_geo_data`

Puebla datos de referencia geográfica (países, provincias, municipios):

```bash
# Crear datos de ejemplo para Cuba con 16 provincias y 166 municipios
python manage.py populate_geo_data --create-sample

# Cargar datos desde archivo JSON
python manage.py populate_geo_data --fixture ruta/a/fixture.json

# Limpiar todos los datos geográficos existentes antes de cargar nuevos datos
python manage.py populate_geo_data --clear --create-sample
```

**Datos de Ejemplo**: Incluye la jerarquía geográfica completa de Cuba (Artemisa, Camagüey, Ciego de Ávila, Cienfuegos, Granma, Guantánamo, Holguín, La Habana, Las Tunas, Matanzas, Mayabeque, Pinar del Río, Sancti Spíritus, Santiago de Cuba, Villa Clara, Isla de la Juventud).

📚 [Guía Completa de Configuración Geográfica](docs/GEO_SETUP_ES.md)

---

## ⚙️ Configuración

### Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
DEBUG=True
# Este proyecto usa `django_settings_env` que por defecto aplica el prefijo `DJANGO_`.
# Define la clave secreta como `DJANGO_SECRET_KEY`; se cargará en la configuración `SECRET_KEY`.
DJANGO_SECRET_KEY=tu-clave-secreta-aqui
DEFAULT_FROM_EMAIL=noreply@isowo.com
EMAIL_HOST=smtp.ejemplo.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@ejemplo.com
EMAIL_HOST_PASSWORD=tu-contraseña
```

### Configuración de Email

Por defecto, los emails se envían a la consola (desarrollo). Para producción:

- Actualiza la configuración `EMAIL_*` en `.env` o `settings.py`
- O configura los ajustes SMTP

### Autenticación Social

Configura los proveedores sociales en el admin de Django:

1. Ve a `/admin/sites/site/` y establece el dominio de tu sitio
2. Ve a `/admin/socialaccount/socialapp/` y agrega apps de Facebook/Google
3. Actualiza las credenciales en `settings.py` o `.env`

---

## 🌍 Soporte Multiidioma

El proyecto soporta múltiples idiomas usando el sistema i18n de Django:

- **Idiomas**: Inglés (por defecto), Español
- **Archivos de traducción**: Carpeta `locale/`
- **Cambio de idioma**: Disponible en la interfaz

📘 [Guía de Configuración](docs/multilanguage_setup_ES.md)

---

## 📝 Notas Importantes

- **Base de Datos**: Usa SQLite para desarrollo. Para producción, cambia a PostgreSQL
- **Archivos Estáticos**: Ejecuta `python manage.py collectstatic` antes del despliegue
- **Archivos Media**: Configura almacenamiento apropiado (S3, CDN) para producción
- **Seguridad**: Establece `DEBUG=False` y configura `ALLOWED_HOSTS` para producción
- **Migraciones**: Siempre crea migraciones después de cambios en modelos: `python manage.py makemigrations`

---

## 🛡 Moderación y Admin

- **Capacidades de moderador**: Los usuarios en el grupo `Moderator` (o `staff`/superusuarios) pueden gestionar anuncios desde el panel de administración: cambiar categoría, modificar campos o eliminar anuncios que infrinjan las políticas.
- **Notificaciones al propietario**: Cuando un moderador cambia la categoría de un anuncio o lo elimina, el sistema intentará notificar por correo al propietario (solo usuarios registrados con email configurado).
- **Acción del admin**: En el listado del admin de `Ad` hay una acción llamada `Notify owner(s) about moderation action` para enviar avisos genéricos a los propietarios seleccionados.

## ☁ CI y Pruebas

- El workflow de CI se consolidó en un único job con matriz (`.github/workflows/ci.yml`) que ejecuta pruebas en las versiones de Python soportadas.
- Forma recomendada de ejecutar pruebas localmente: `pytest` (con `pytest-django`). Para ejecutar con la configuración de Django explícita, usa:

```bash
# recomendado: ejecutar pruebas con la variable DJANGO_SETTINGS_MODULE
DJANGO_SETTINGS_MODULE=config.settings poetry run pytest -q
```


## 🧪 Desarrollo

### Ejecutar Pruebas

```bash
pytest
```

### Formateo de Código

```bash
ruff check .
ruff format .
```

### Pre-commit Hooks

```bash
pre-commit install
```

---

## 📚 Documentación

- [Comandos Personalizados](docs/commands/)
- [Configuración Geográfica y Búsqueda Basada en Ubicación](docs/GEO_SETUP_ES.md)
- [Configuración Multiidioma](docs/multilanguage_setup_ES.md)
- [README en Inglés](README.md)

---

## 🤝 Contribuir

1. Crea nuevas apps usando el comando `startapp_in_apps`
2. Sigue las mejores prácticas de Django
3. Escribe pruebas para nuevas características
4. Mantén el directorio `apps/` limpio y modular

---

## 📄 Licencia

Apache License 2.0 - Ver el archivo [LICENSE](LICENSE) para más detalles.

---

## 👤 Autores

**kmilo** - <kmilo.denis.glez@yandex.com>
