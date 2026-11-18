# PWDigital

PWDigital is a Django-based digital PWD ID and verification system prototype. This implementation includes project setup and the Account Feature only.

## Requirements

- Python 3.12+
- PostgreSQL 14+ or Supabase PostgreSQL
- VS Code or another terminal environment

## Setup

1. Create a virtual environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and provide real values.

3. Create a PostgreSQL database, for example:
   ```sql
   CREATE DATABASE pwdigital;
   ```

4. Run migrations:
   ```powershell
   python manage.py migrate
   python manage.py createsuperuser
   ```

The initial migration creates the Applicant, LGU_Staff, Partner, and Admin roles. `createsuperuser` assigns the Admin role automatically.

For Supabase, set `DATABASE_URL` to the Supabase PostgreSQL connection URL and set `DATABASE_SSL_REQUIRE=True`.

SQLite is intentionally unsupported.

## Run

```powershell
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

## Tests

Configure a real PostgreSQL test database in `.env`, then run:

```powershell
python manage.py test
```
