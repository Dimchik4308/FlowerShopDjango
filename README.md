# PetalBloom Flower Shop

A Django-based flower shop e-commerce application with product variants, cart and order management, Stripe checkout, email verification, subscriber support, and an admin panel.

## Features

- Product catalog with variants, colors, sizes, and images
- Add to cart, remove from cart, and checkout flows
- Order creation and user order history
- Stripe payment integration and webhook support
- Email verification for new user registration
- Password reset via email
- Subscriber newsletter capture
- Optional AWS S3 media storage support via `django-storages`
- AI chat API endpoint at `/api/chat/`

## Tech Stack

- Python 3
- Django 6.0.3
- PostgreSQL
- Stripe payments
- Docker / Docker Compose
- pytest / pytest-django

## Requirements

Install dependencies from `requirements.txt`.

## Environment Variables

The project reads configuration from environment variables. Common variables include:

- `SECRET_KEY`
- `DEBUG` (default is `True` in settings, but should be `False` in production)
- `ALLOWED_HOSTS`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`
- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `DEFAULT_FROM_EMAIL`
- `STRIPE_PUBLIC`
- `STRIPE_SECRET`
- `AWS_ACCESS_KEY_ID` (optional)
- `AWS_SECRET_ACCESS_KEY` (optional)
- `AWS_STORAGE_BUCKET_NAME` (optional)
- `AWS_S3_REGION_NAME` (optional, default `eu-north-1`)

If AWS storage variables are provided, media files are served from S3. Otherwise, the app uses local `media/` storage.

## Running with Docker

Start the app using Docker Compose:

```bash
docker compose up --build
```

The web service is exposed on port `8005` by default.

## Local Development

The application is designed to run via Docker Compose.

1. Build and start services:

```bash
docker compose up --build
```

2. Apply migrations inside the running web container:

```bash
docker compose exec web python manage.py migrate
```

3. Create a superuser inside the running web container:

```bash
docker compose exec web python manage.py createsuperuser
```

4. Open the app in your browser at `http://localhost:8005`

## Application Endpoints

- `/` — home/catalog
- `/good/<slug>/` — product detail
- `/good/<slug>/buy` — buy product flow
- `/checkout/` — checkout cart
- `/payment/<order_id>` — Stripe payment session
- `/my_orders/` — user order history
- `/register/` — register
- `/login/` — login
- `/logout/` — logout
- `/password_reset/` — password reset
- `/verify/<uidb64>/<token>/` — email verification
- `/api/chat/` — AI chat endpoint

## Testing

Run tests with:

```bash
pytest
```

## Notes

- `DEBUG` is enabled in the current settings, so set it to `False` for production deployments.
- Ensure `SECRET_KEY` and all credentials are kept out of source control.
- Static files are collected to `staticfiles/` and application static assets are stored in `main/static/`.

## Project Structure

- `DjangoFlowerShop/` — Django project settings and WSGI configuration
- `main/` — main app containing models, views, templates, forms, and business logic
- `templates/main/` — site templates
- `static/main/` — frontend assets
- `docker-compose.yml` — container orchestration config
- `requirements.txt` — Python dependencies
