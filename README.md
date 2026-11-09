# Medium

A Medium-inspired web application built with Django. Users can create accounts, publish articles, and manage their profiles.

## Current setup

- Python 3.12
- Django 5.2
- PostgreSQL 16
- Docker Compose for local development

The legacy CKEditor integration has temporarily been replaced with a plain text field.

> This setup is for local development only. It uses Django's development server and is not ready for public production deployment.

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

These instructions require the Docker configuration files to be present in your checked-out branch. While the deployment work is on a separate branch, check it out:

```bash
git switch deployment-setup
```

### 2. Create the local environment file

```bash
cp .env.example .env.local
```

The example file should contain nonempty placeholders:

```dotenv
DJANGO_SECRET_KEY=replace-with-a-new-random-key
DJANGO_DEBUG=True
POSTGRES_PASSWORD=replace-with-your-local-database-password
```

If these variables were previously exported in your terminal, clear them so Compose uses the file values:

```bash
unset DJANGO_SECRET_KEY DJANGO_DEBUG POSTGRES_PASSWORD
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
- Keep `DJANGO_DEBUG=True` for local development only.

Single-quote passwords containing special characters such as `$`, `#`, or spaces:

```dotenv
POSTGRES_PASSWORD='replace-with-your-own-password'
```

Never commit `.env.local` or share its contents. Keep only placeholders in `.env.example`.

> For an existing database volume, use its current password. Changing this file does not reset an existing database password. See the password-change section below.

### 4. Start the services

```bash
docker compose --env-file .env.local up -d
```

Check their status:

```bash
docker compose --env-file .env.local ps
```

Wait for the database service to become healthy.

### 5. Apply database migrations

```bash
docker compose --env-file .env.local exec web python manage.py migrate
```

Run this for a fresh database and after pulling changes that include new migrations. It is not necessary on every startup.

### 6. Create an administrator

```bash
docker compose --env-file .env.local exec web python manage.py createsuperuser
```

Follow the prompts and keep your password private.

### 7. Open the application

- Application: http://localhost:8000/
- Administration: http://localhost:8000/admin/

## Everyday commands

Run all commands from the project directory.

### Start services

```bash
docker compose --env-file .env.local up -d
```

### Rebuild after dependency or Dockerfile changes

```bash
docker compose --env-file .env.local up -d --build web
```

The project directory is bind-mounted into the web container. Ordinary Python code changes are usually picked up by Django's development reloader without rebuilding.

### View logs

```bash
docker compose --env-file .env.local logs --tail=50 web
docker compose --env-file .env.local logs --tail=50 db
```

Follow web logs:

```bash
docker compose --env-file .env.local logs -f web
```

Press Ctrl+C to stop following logs. This does not stop the services.

### Run system checks

```bash
docker compose --env-file .env.local exec web python manage.py check
```

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

The project currently has no automated tests. A run with zero tests does not verify application behavior.

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

> Do not add `-v` unless you intentionally want to delete the database volume and its data.

## Database connection

| Application location | Database host | Database port |
| --- | --- | --- |
| Inside the `web` container | `db` | `5432` |
| Directly in WSL or on the host | `127.0.0.1` | `5433` |

The database and database user are both named `medium_dev`.

PostgreSQL is published only on the local loopback interface. Database data is stored in a named Docker volume and survives container recreation. A volume is not a backup.

Uploaded media is stored in the project's local `media/` directory through the development bind mount. Back up media separately from the database.

## Environment variables

The `--env-file .env.local` option provides values for Compose variable substitution. The service's `environment` settings pass the required values to its container.

Editing `.env.local` does not automatically update a running container.

After changing web settings, recreate the web container:

```bash
docker compose --env-file .env.local up -d --force-recreate web
```

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

docker compose --env-file .env.local up -d --force-recreate db web

docker compose --env-file .env.local exec web \
  python manage.py showmigrations --database default
```

Applied migrations should be marked `[X]`.

Do not delete the database volume to fix a password mismatch.

## Troubleshooting

### Connection refused

Check that Docker is running and the database is healthy:

```bash
docker compose --env-file .env.local ps
docker compose --env-file .env.local logs --tail=50 db
```

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

Stop any Django server running directly in WSL, or another application using port 8000, then start the web service again.

### Required environment variable is missing

Ensure `.env.local` exists, its required values are nonempty, and the Compose command includes `--env-file .env.local`.

## Security and production status

- Never commit real passwords, secret keys, or local environment files.
- Credentials previously committed to a public repository must be rotated. Removing a file from the latest commit does not remove it from history.
- Avoid sharing `docker compose config` output because it can contain resolved secrets.
- `DJANGO_DEBUG=True` is only for local development.
- The current configuration uses Django's development server, not a production application server.
- Production deployment still requires appropriate host settings, static and media file handling, HTTPS, secret management, backups, and a security review.
