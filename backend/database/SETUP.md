
# Database Setup

SalesGenie uses PostgreSQL for its database and Alembic to manage schema migrations.

The database tables are created through migrations. You do not need to create them manually.

For general installation instructions, see the [main Setup Guide](../../SETUP.md).

## Prerequisites

- Complete the main project setup.
- Docker and Docker Compose must be installed and running.
- The Python virtual environment must be activated.
- Run commands from the repository root.

## 1. Start the Database

```bash
docker compose up -d db
```

Check the database status:

```bash
docker compose ps
```

Wait until the database is healthy before continuing.

## 2. Initialize the Database

Apply all pending migrations:

```bash
alembic upgrade head
```

This creates the required tables and updates the database to the latest migration version.

You only need to run this again when new migrations have been added.

## 3. Verify the Database

Open a PostgreSQL shell:

```bash
docker compose exec db psql -U salesgenie -d salesgenie
```

List the tables:

```sql
\dt
```

Inspect a table:

```sql
\d leads
```

Exit the shell:

```sql
\q
```

The tables depend on the committed migrations. You should also see `alembic_version`, which tracks the current migration revision.

## 4. Common Commands

| Task | Command |
|---|---|
| Start the database | `docker compose up -d db` |
| Stop containers | `docker compose down` |
| View database logs | `docker compose logs -f db` |
| Check current migration | `alembic current` |
| View migration history | `alembic history` |
| Apply pending migrations | `alembic upgrade head` |

Stopping containers with `docker compose down` normally preserves the database volume and its data.

## 5. Making Database Changes

Database schema changes should be coordinated with the person responsible for the database.

The usual workflow is:

1. Update the relevant SQLAlchemy model in `backend/database/models/`.
2. Generate a migration:

   ```bash
   alembic revision --autogenerate -m "describe the change"
   ```

3. Review the generated file in `migrations/versions/`.
4. Apply the migration:

   ```bash
   alembic upgrade head
   ```

5. Commit the model changes and migration file together.

Do not manually create tables or use `Base.metadata.create_all()` to initialize the database. Use Alembic migrations instead.

## Troubleshooting

### Database connection refused

Check that the database is running:

```bash
docker compose ps
docker compose logs db
```

Wait for PostgreSQL to become healthy and check your database configuration.

### Port 5432 is already in use

If another PostgreSQL instance is using port 5432, configure a different host port in the root `.env` file, provided the Compose configuration supports `DB_PORT`.

For example:

```ini
DB_PORT=5433
```

Restart the database if necessary.

### Tables are missing

Run the migration command from the repository root:

```bash
alembic upgrade head
```

If the problem persists, check the migration history and database connection settings.

### Python cannot find the backend module

Make sure the virtual environment is activated and your terminal is in the repository root.

---

For installation, environment configuration, and running the application, see the [main Setup Guide](../../SETUP.md).
