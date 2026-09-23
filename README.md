# Medihub

A healthcare platform backend built with Django REST Framework for Bangladesh, connecting patients with doctors, blood donors, ambulances, pharmacies, and diagnostic centers.

## Features

- **Authentication** — JWT-based auth with OTP verification and two-factor support
- **Doctor Profiles** — Search doctors by specialization, location, and availability; book appointments
- **Blood Donors** — Find blood donors by blood group and location
- **Ambulance** — Locate and contact ambulance services
- **Pharmacy** — Find nearby pharmacies
- **Diagnostic Centers** — Browse diagnostic centers and available tests
- **Posts & Feed** — Community posts for blood needs, medicine needs, equipment needs, and general health posts with a smart feed engine
- **Blog** — Health articles with likes and comments
- **Notifications** — In-app and Firebase push notifications
- **Location** — Bangladesh administrative hierarchy (Division → District → Upazila → Union)
- **Monitoring** — Prometheus metrics, Grafana, and Promtail log shipping

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 4.2, Django REST Framework |
| Auth | JWT (SimpleJWT) |
| Database | PostgreSQL 16 |
| Cache / Queue | Redis 7, Celery |
| Storage | Local / AWS S3 (django-storages) |
| Push Notifications | Firebase Admin SDK |
| Payments | Stripe |
| API Docs | Swagger (drf-yasg) |
| Web Server | Gunicorn + Nginx |
| Containerization | Docker, Docker Compose |
| CI/CD | GitHub Actions |
| Monitoring | Prometheus, Alertmanager, Promtail |

## Project Structure

```
medihub/          # Django project settings, celery, urls
authentication/   # User registration, login, OTP, JWT
profiles/         # Doctor, donor, ambulance, pharmacy, diagnostic profiles
doctor/           # Doctor search & listing API
donor/            # Blood donor search API
ambulance/        # Ambulance search API
pharmacy/         # Pharmacy search API
diagnostic/       # Diagnostic center & test API
post/             # Community posts (blood, medicine, equipment, general)
blog/             # Blog posts, comments, likes
feed/             # Smart feed engine
notification/     # App & push notifications
interactions/     # User-doctor interactions
location/         # Division, district, upazila, union data
cache/            # Redis cache services
core/             # Shared utilities, permissions, pagination
monitoring/       # Prometheus, Alertmanager, Promtail configs
```

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Python 3.11+

### Local Setup (without Docker)

```bash
# Clone the repo
git clone <repo-url>
cd Medihub

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env .env.local
# Edit .env with your local DB credentials

# Run migrations
python manage.py migrate

# Seed initial data
python manage.py seed_data

# Start server
python manage.py runserver
```

### Docker Setup (Recommended)

```bash
# Development
docker compose -f docker-compose.dev.yml up --build

# Production
docker compose -f docker-compose.prod.yml up --build
```

The API will be available at `http://localhost:8000`.

## Environment Variables

Copy `.env` and update the following key variables:

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DB_*` | PostgreSQL connection settings |
| `REDIS_*` | Redis connection settings |
| `JWT_SECRET_KEY` | JWT signing key |
| `EMAIL_*` | SMTP email configuration |
| `AWS_*` | S3 storage (set `USE_S3=True` to enable) |
| `STRIPE_*` | Stripe payment keys |
| `FIREBASE_CREDENTIALS_PATH` | Path to Firebase service account JSON |

> **Never commit `.env` to version control.**

## API Documentation

Swagger UI is available at:

```
http://localhost:8000/swagger/
```

## Key Endpoints

| Prefix | Module |
|---|---|
| `/authentication/` | Register, login, OTP, token refresh |
| `/api/v1/doctors/` | Doctor search & profiles |
| `/api/v1/donors/` | Blood donor search |
| `/api/v1/ambulances/` | Ambulance listings |
| `/api/v1/pharmacies/` | Pharmacy listings |
| `/api/v1/diagnostics/` | Diagnostic centers & tests |
| `/profiles/` | User & service provider profiles |
| `/posts/` | Community posts |
| `/blogs/` | Blog articles |
| `/notification/` | Notifications |
| `/location/` | Location hierarchy |
| `/health/` | Health check |

## Running Tests

```bash
python manage.py test --settings=medihub.test_settings
```

## CI/CD

GitHub Actions workflows are defined in `.github/workflows/`:
- `ci.yml` — runs tests on every push
- `cicd.yml` — builds and deploys on merge to main
