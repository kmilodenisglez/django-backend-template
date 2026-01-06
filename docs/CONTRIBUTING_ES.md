# Contribuyendo

¡Gracias por contribuir a Isowo! Esta breve guía te ayuda a configurar un entorno de desarrollo local, seguir las reglas de estilo del proyecto y enviar pull requests de alta calidad.

## Configuración para desarrolladores

1. Instala las dependencias (se recomienda Poetry):

```bash
poetry install --no-interaction --no-ansi
```

2. Inicializa las herramientas y los hooks:

```bash
make bootstrap
make install-pre-commit
```

3. Aplica formateo y linting localmente:

```bash
make format
make lint
```

4. Ejecuta pruebas:

```bash
make test
```

## Trabajando en cambios

- Crea una rama por característica o corrección: `git checkout -b feature/mi-caracteristica`
- Mantén commits pequeños y enfocados. Usa mensajes descriptivos.
- Ejecuta `make precommit-all` antes de abrir un PR para aplicar los hooks en todos los archivos.

## Lista de comprobación para Pull Requests

- [ ] Pruebas añadidas o actualizadas para un comportamiento nuevo
- [ ] Todas las comprobaciones pasan (Ruff, hooks de pre-commit, pytest)
- [ ] Documentación actualizada si es necesario

## Estilo y herramientas

- Ruff se usa para linting y formateo. Usa `make format` y `make lint` localmente.
- Los hooks de pre-commit ejecutan Ruff en los commits y previenen problemas comunes (espacios finales, línea final, archivos grandes).

## Notas

Si necesitas un entorno específico (p.ej. PostgreSQL u otros servicios), documenta en el issue o PR correspondiente. ¡Gracias por ayudar a mejorar Isowo!
