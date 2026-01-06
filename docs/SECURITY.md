**Security Checklist & Environment Variables**

- **Purpose:** This document lists recommended security configuration, environment variables, and deployment guidance for Isowo. Keep secrets out of source control and set these variables in your deployment environment (systemd unit, container secrets, CI/CD vault, etc.).

- **Generate a secure SECRET_KEY (example):**

```bash
python - <<'PY'
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
PY
```

Copy the output and set it as `DJANGO_SECRET_KEY` (see examples below).

- **Important environment variables (recommended names)**

Use the `DJANGO_` prefix where applicable. This project uses `django_settings_env.Env` which will prefix variables automatically, but examples below show the explicit variable names used by that package when a prefix is applied.

# Core
DJANGO_SECRET_KEY=replace_with_generated_secret
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=example.com,www.example.com

# HTTPS / cookies / HSTS
DJANGO_SECURE_SSL_REDIRECT=True  # Redirect HTTP to HTTPS in production
DJANGO_SESSION_COOKIE_SECURE=True
DJANGO_CSRF_COOKIE_SECURE=True
DJANGO_SECURE_HSTS_SECONDS=3600  # Start small; 31536000 = 1 year when ready
DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS=True
DJANGO_SECURE_HSTS_PRELOAD=False  # Be careful: `preload` has long-term impact
DJANGO_USE_PROXY_SSL_HEADER=True  # If behind TLS-terminating proxy

# Email (example)
DJANGO_DEFAULT_FROM_EMAIL=noreply@example.com
DJANGO_EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
DJANGO_EMAIL_HOST=smtp.example.com
DJANGO_EMAIL_PORT=587
DJANGO_EMAIL_USE_TLS=True
DJANGO_EMAIL_HOST_USER=your_smtp_user
DJANGO_EMAIL_HOST_PASSWORD=your_smtp_password

# Social / Payment credentials (examples)
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
FACEBOOK_CLIENT_ID=...
FACEBOOK_CLIENT_SECRET=...
INSTAGRAM_CLIENT_ID=...
INSTAGRAM_CLIENT_SECRET=...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
NOWPAYMENTS_API_KEY=...

- **Deployment Recommendations**

- Set `DJANGO_DEBUG=False` and configure `DJANGO_ALLOWED_HOSTS` for production.
- Keep `DJANGO_SECRET_KEY` secret. Do not commit it. Use deployment secrets (Docker secrets, systemd `Environment=`, or a secrets manager).
- Start HSTS with a small timeout (3600) while validating HTTPS across all hosts/subdomains. Only set `SECURE_HSTS_PRELOAD=True` after reading the documentation and validating subdomains.
- If your load balancer terminates TLS, enable `DJANGO_USE_PROXY_SSL_HEADER` and configure the proxy to set `X-Forwarded-Proto: https`.
- Use secure cookies (`SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`) so cookies are sent only over HTTPS.
- Run periodic secret rotation if possible, and maintain an incident response plan for key leakage.
- Consider adding Content Security Policy (CSP) headers and other HTTP security headers (Referrer-Policy, X-Frame-Options already set by Django), using middleware or your web server.

- **Local Development Tips**

- You may keep `DJANGO_DEBUG=True` for local development, but never enable it in production.
- Use a separate `.env` for local development with safe defaults; do not copy production secrets.
- The `.env.example` file shows typical variables and safe placeholders.

- **Checking configuration**

Run Django's deployment checks to validate settings:

```bash
poetry run python manage.py check --deploy
```

Address warnings before publishing a production instance.

- **Where to set variables**

- Docker: use Docker secrets or `--env-file` for non-secret local values.
- systemd: use `Environment=` or `EnvironmentFile=` with appropriate permissions.
- Kubernetes: use Secrets and mount them as env vars or files.

- **Contact & Notes**

If you need assistance wiring these variables into your CI/CD or host, I can produce example systemd unit snippets, Docker Compose overrides, or Kubernetes Secret manifests.
