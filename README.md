# Medium

A Medium-inspired web application built with Django. Users can create accounts, publish articles, and manage their profiles.

## Current setup

- Python 3.12
- Django 5.2
- PostgreSQL 16
- Docker Compose for local development and deployment preparation
- Gunicorn as the Django application server
- Nginx as a reverse proxy and uploaded-media server
- WhiteNoise for collected static files

The legacy CKEditor integration has temporarily been replaced with a plain text field.

> This configuration has been tested locally with `DJANGO_DEBUG=False`. Using Gunicorn and Nginx does not, by itself, make the project ready for public production deployment. HTTPS, backups, upload security, and a full deployment security review are still required.

## Prerequisites

- Git
- Docker with Docker Compose v2
- On Windows: Docker Desktop with WSL 2 integration enabled

Run the commands from your project directory in a Linux or WSL terminal. On Windows, keeping the project in the WSL Linux filesystem is recommended.

## First-time setup

### 1. Clone the repository

```bash
git clone https://github.com/saadat99/medium.git
cd medium
```

These instructions require the updated Docker and Nginx configuration files to be present in your checked-out branch. While the deployment work is on a separate branch, check it out after it has been pushed to the repository:

```bash
git switch deployment-setup
```

### 2. Create the local environment file

```bash
cp .env.example .env.local
```

The example file should contain nonempty placeholders for required secrets and local host settings:

```dotenv
DJANGO_SECRET_KEY=replace-with-a-new-random-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS="localhost 127.0.0.1 [::1]"
POSTGRES_PASSWORD=replace-with-your-local-database-password
```

If these variables were previously exported in your terminal, clear them so Compose uses the file values:

```bash
unset DJANGO_SECRET_KEY DJANGO_DEBUG DJANGO_ALLOWED_HOSTS POSTGRES_PASSWORD
```

### 3. Build the web image and generate a secret key

```bash
docker compose --env-file .env.local build web
```

Generate a new Django secret key:

```bash
docker compose --env-file .env.local run --rm --no-deps web \
  python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Edit `.env.local`:

- Set `DJANGO_SECRET_KEY` to the generated value.
- Set `POSTGRES_PASSWORD` to a strong, unique local database password.
- Keep `DJANGO_DEBUG=False` for testing the current Gunicorn and Nginx setup.
- Keep the local hostnames in `DJANGO_ALLOWED_HOSTS`. Values are separated by spaces and must not include a URL scheme or port.

Single-quote passwords containing special characters such as `$`, `#`, or spaces:

```dotenv
POSTGRES_PASSWORD='replace-with-your-own-password'
```

Never commit `.env.local` or share its contents. Keep only placeholders and non-sensitive example settings in `.env.example`.

> For an existing database volume, use its current password. Changing this file does not reset an existing database password. See the password-change section below.

### 4. Prepare media storage and start the services

```bash
mkdir -p media

docker compose --env-file .env.local up -d --build
```

Docker downloads the PostgreSQL and Nginx images if they are not already available.

Check service status:

```bash
docker compose --env-file .env.local ps
```

The `db`, `web`, and `nginx` services should be running. The database should become healthy. A started container alone does not guarantee that the application is ready; check the logs if requests fail.

### 5. Apply database migrations

```bash
docker compose --env-file .env.local exec web python manage.py migrate
```

Run this for a fresh database and after pulling changes that include new migrations. It is not necessary on every startup.

### 6. Collect static files

```bash
docker compose --env-file .env.local exec web \
  python manage.py collectstatic --noinput
```

Restart Gunicorn so WhiteNoise discovers the collected files:

```bash
docker compose --env-file .env.local restart web
```

Repeat this step after changes to static assets or dependencies that provide them.

### 7. Create an administrator

```bash
docker compose --env-file .env.local exec web python manage.py createsuperuser
```

Follow the prompts and keep your password private. Skip this step if an administrator account already exists.

### 8. Open the application

- Application: http://127.0.0.1:8000/
- Administration: http://127.0.0.1:8000/admin/
- Static-file check: http://127.0.0.1:8000/static/admin/css/base.css

## Request routing

```text
Browser -> Nginx at 127.0.0.1:8000
              |
              +-- /media/ -> uploaded files in the local media/ directory
              |
              +-- other requests -> Gunicorn -> Django / WhiteNoise
```

- Nginx publishes container port `80` as host port `8000`, bound only to `127.0.0.1`.
- Gunicorn listens on `0.0.0.0:8000` inside the `web` container. Its port is not directly published to the host.
- WhiteNoise serves files collected into `staticfiles/`.
- Nginx reads uploaded media through a read-only mount at `/var/www/media`.
- Django writes uploaded files through the project bind mount at `/app/media`.
- Django's development-only media URL helper does not serve uploads when `DEBUG=False`.

## Everyday commands

Run all commands from the project directory.

### Start services, including after a reboot

Ensure Docker is running first. On Windows, start Docker Desktop and wait for it to be ready.

```bash
docker compose --env-file .env.local up -d
```

The Compose configuration now starts Gunicorn automatically. A separate `docker compose run ... gunicorn` command is no longer needed.

### Rebuild after dependency or Dockerfile changes

```bash
docker compose --env-file .env.local up -d --build
```

The project directory is bind-mounted into the web container, but Gunicorn does not use Django's development reloader. Restart the web service after ordinary Python code changes:

```bash
docker compose --env-file .env.local restart web
```

If static assets changed, also run `collectstatic` before restarting the web service.

### Check service status

```bash
docker compose --env-file .env.local ps
```

Include stopped containers:

```bash
docker compose --env-file .env.local ps -a
```

### View logs

```bash
docker compose --env-file .env.local logs --tail=80 web nginx
docker compose --env-file .env.local logs --tail=50 db
```

Follow application and proxy logs:

```bash
docker compose --env-file .env.local logs -f web nginx
```

Press Ctrl+C to stop following logs. This does not stop the services.

### Validate configuration

Check Compose configuration without printing resolved secrets:

```bash
docker compose --env-file .env.local config --quiet
```

Test Nginx configuration while its container is running:

```bash
docker compose --env-file .env.local exec nginx nginx -t
```

After editing `nginx/default.conf`, test it and then reload Nginx:

```bash
docker compose --env-file .env.local exec nginx nginx -t && \
docker compose --env-file .env.local exec nginx nginx -s reload
```

### Run system checks

```bash
docker compose --env-file .env.local exec web python manage.py check
```

Review deployment-specific warnings separately:

```bash
docker compose --env-file .env.local exec web python manage.py check --deploy
```

A successful basic check does not establish production readiness. Evaluate deployment warnings against the intended server environment.

### Confirm debug mode

```bash
docker compose --env-file .env.local exec web \
  python manage.py shell -c "from django.conf import settings; print('DEBUG =', settings.DEBUG)"
```

For the current setup, the expected value is `False`.

### Check for model changes without creating migrations

```bash
docker compose --env-file .env.local exec web \
  python manage.py makemigrations --check --dry-run
```

### Show migration status

```bash
docker compose --env-file .env.local exec web python manage.py showmigrations
```

### Run tests

```bash
docker compose --env-file .env.local exec web python manage.py test
```

No automated tests were discovered during the initial setup. A run with zero tests does not verify application behavior.

### Open the Django shell

```bash
docker compose --env-file .env.local exec web python manage.py shell
```

### Stop services without removing containers

```bash
docker compose --env-file .env.local stop
```

### Remove containers and the Compose network, retaining database data

```bash
docker compose --env-file .env.local down
```

> Do not add `-v` unless you intentionally want to delete the database volume and its data and have verified backups.

## Database connection and file storage

| Application location | Database host | Database port |
| --- | --- | --- |
| Inside the `web` container | `db` | `5432` |
| Directly in WSL or on the host | `127.0.0.1` | `5433` |

The database and database user are both named `medium_dev`.

PostgreSQL is published only on the local loopback interface. Database data is stored in the named Docker volume `medium_dev_pgdata` and survives normal container recreation. Compose may prefix the actual volume name with the project name.

| Data | Location | Notes |
| --- | --- | --- |
| Database | PostgreSQL named volume | Retained by ordinary `stop` and `down` commands |
| Uploaded media | Project `media/` directory | Shared with Django; mounted read-only in Nginx |
| Collected static files | Project `staticfiles/` directory | Generated by `collectstatic`; excluded from Git |
| Local environment settings | `.env.local` | Must not be committed |

A persistent volume or bind mount is not a backup. Back up uploaded media separately from the database. Do not include user uploads in infrastructure commits.

## Environment variables

The `--env-file .env.local` option provides values for Compose variable substitution. The service's `environment` settings pass the required values to its container; the option does not automatically forward every variable in the file.

Django reads the allowed hosts using:

```python
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split()
```

When adding a new environment setting, review all three locations:

1. The code that reads it.
2. The Compose configuration that passes it to the service.
3. `.env.example`, which documents a safe example or placeholder.

Editing `.env.local` does not automatically update a running container. After changing web settings, recreate the web container and Nginx:

```bash
docker compose --env-file .env.local up -d --force-recreate web nginx
```

Recreating Nginx also ensures it resolves the current web container address.

Changing `DJANGO_SECRET_KEY` invalidates existing signed sessions, so users may need to log in again.

Commands in this README run Django inside Docker. A Python virtual environment on the host is not required for this workflow. Running Django directly on the host requires installing dependencies and separately providing the required environment variables; Django does not automatically read `.env.local`.

## Changing an existing database password

`POSTGRES_PASSWORD` sets the initial database user password only when PostgreSQL initializes an empty data directory. Changing it in `.env.local` alone does not change an existing database password.

### 1. Change the actual PostgreSQL password

```bash
docker compose --env-file .env.local exec db \
  psql -U medium_dev -d medium_dev
```

Inside PostgreSQL:

```text
\password medium_dev
```

Enter and confirm the new password, then exit:

```text
\q
```

### 2. Update the application password

Set `POSTGRES_PASSWORD` in `.env.local` to exactly the same new password.

### 3. Recreate containers and verify the connection

```bash
unset POSTGRES_PASSWORD

docker compose --env-file .env.local up -d --force-recreate db web nginx

docker compose --env-file .env.local exec web \
  python manage.py showmigrations --database default
```

Applied migrations should be marked `[X]`.

Do not delete the database volume to fix a password mismatch.

## Troubleshooting

### No pages load or connection is refused

Check that Docker is running and inspect all service states:

```bash
docker compose --env-file .env.local ps -a
docker compose --env-file .env.local logs --tail=80 web nginx db
```

If the services were not created or updated, run:

```bash
docker compose --env-file .env.local up -d --build
```

Inspect this command's output for image-download, build, mount, or port errors. Old logs from a stopped `runserver` container do not describe the current Gunicorn setup.

### Nginx image has not been downloaded

Run the startup command and allow the image pull to finish. If it fails, inspect the actual Docker error. You can retry the image download separately:

```bash
docker compose --env-file .env.local pull nginx
```

Then start the services again.

### Bad Request (400)

Check `DJANGO_ALLOWED_HOSTS` and the application logs. For the local setup:

```dotenv
DJANGO_ALLOWED_HOSTS="localhost 127.0.0.1 [::1]"
```

Do not include `http://`, `https://`, or a port number. Recreate the web and Nginx containers after changing the environment. Do not use a wildcard allowed-host setting as a workaround.

### Nginx returns 502 Bad Gateway

Check that Gunicorn is running and listening on `0.0.0.0:8000` inside `web`:

```bash
docker compose --env-file .env.local logs --tail=80 web nginx
```

If `web` was recreated and Nginx still targets its old address, restart Nginx:

```bash
docker compose --env-file .env.local restart nginx
```

### Uploaded images do not load

- Confirm the image URL starts with `/media/`.
- Verify that the corresponding file exists in the project's `media/` directory.
- Check Nginx logs for missing-file or permission errors.
- Verify the media directory is mounted at `/var/www/media` in Nginx and the files are readable.

WhiteNoise is not responsible for uploaded media. Do not enable Django debug mode to fix media delivery.

### Static files or administration styles do not load

Run:

```bash
docker compose --env-file .env.local exec web \
  python manage.py collectstatic --noinput

docker compose --env-file .env.local restart web
```

Refresh the browser without its cached assets. WhiteNoise should be configured immediately after Django's `SecurityMiddleware`.

### Upload returns 413 Request Entity Too Large

The current Nginx configuration sets `client_max_body_size 10m`. This limits the entire request body, not just an individual file. Review application upload validation and requirements before changing this limit.

### Password authentication failed

The password sent by Django does not match the actual PostgreSQL password. Follow the password-change instructions to synchronize them. Also ensure an exported terminal variable is not overriding the file value.

### Package download timeout during build

Check the network connection and Docker Desktop proxy settings, if applicable. The Dockerfile uses an extended pip download timeout.

Retry:

```bash
docker compose --env-file .env.local --progress=plain build web
```

Do not disable HTTPS certificate verification to work around network issues.

### Port 8000 is already in use

Stop any old manual Gunicorn container, Django server running directly in WSL, or other application using port 8000. In the current configuration, Nginx is the service that publishes this port.

Do not run the previous manual `docker compose run --service-ports ... gunicorn` workflow alongside this setup.

### Required environment variable is missing

Ensure `.env.local` exists, its required values are nonempty, and the Compose command includes `--env-file .env.local`.

## Security and production status

- Never commit real passwords, secret keys, or local environment files.
- Credentials previously committed to a public repository must be rotated or revoked. Removing a file from the latest commit does not remove it from history. Review historical secrets before pushing deployment changes.
- Avoid sharing `docker compose config` output because it can contain resolved secrets. Use `config --quiet` for validation.
- Keep `DJANGO_DEBUG=False` for this deployment-preparation workflow. A local smoke test with debug disabled is not a full security audit.
- Gunicorn, WhiteNoise, and Nginx have been tested locally for application requests, static assets, and uploaded media.
- The current project bind mount and local-only port bindings are not a final production architecture.
- Review upload types, validation, response headers, and media isolation before accepting public uploads. A read-only Nginx mount does not make uploaded content safe; consider serving untrusted media from a separate origin.
- Public deployment still requires a real domain, HTTPS, appropriate secure-cookie and proxy settings, secret management, tested database and media backups, container hardening, monitoring, and a security review.
- Review deployment checks and add automated tests before relying on CI/CD. Check whether a push or merge triggers any existing deployment automation.
