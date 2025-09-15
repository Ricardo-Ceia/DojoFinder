# DojoFinder

Find, manage, and promote Judo dojos. DojoFinder is a Flask web app that lets users search dojos by city or near their current location, while dojo owners can create premium listings with schedules, photos, and contact info. Payments are handled via Stripe subscriptions. Admins have a simple dashboard, and users can sign up and log in.

## Features

- Search dojos by city
- “Near me” search using geodesic distance and a bounding box optimization
- Dojo details page with schedules, pricing, images, and instructor info
- User accounts (signup/login) with bcrypt password hashing
- Premium dojo form and Stripe Checkout subscription flow
- Webhook to persist successful premium listings and schedules
- Email notification when a new dojo is listed (Flask-Mail via SMTP)
- Manage and edit your dojos with schedules and images
- Basic admin login and dashboard
- SQLite database with simple setup script

## Tech stack

- Backend: Flask (Python)
- DB: SQLite (via `sqlite3`)
- Payments: Stripe Checkout + Webhooks
- Geocoding/Distance: geopy (Nominatim + geodesic)
- Email: Flask-Mail (SMTP)
- Auth: Sessions + bcrypt hashing
- Caching: cachetools TTLCache (12h) for geocoding results
- Templates: Jinja2 (`templates/`)
- Static assets: `static/` (images and JS)

## Project structure

```
DojoFinder/
├─ app.py                  # Flask app and routes
├─ unit_tests.py           # Basic API tests with unittest
├─ DB/
│  ├─ dojo_listings.db     # SQLite DB (checked in)
│  ├─ set_up_database.py   # Creates DB/tables
│  └─ verify_db.py         # Optional DB checks/utilities
├─ templates/              # Jinja2 templates (HTML pages)
├─ static/                 # Images and front-end JS
└─ uploads/                # User-uploaded images (dojo/sensei)
```

## Getting started

### Prerequisites

- Python 3.10+
- pip
- Stripe account (for payments) if testing premium flow
- SMTP credentials (e.g., Gmail App Password) if testing email sending

### Setup

1) Clone and create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2) Initialize the database (creates tables if missing)

```bash
cd DB
python set_up_database.py
cd ..
```

This generates `dojo_listings.db` in `DB/`. The app reads from `./DB/dojo_listings.db`.

3) Configure settings and secrets

Current demo defaults are hardcoded in `app.py` for simplicity (Stripe keys, Gmail SMTP, admin credentials, etc.). For real use:

- Replace demo values in `app.py` (recommended: refactor to read from environment variables).
- Set `app.config['BASE_URL']` to your host (for Stripe redirects).
- Ensure `UPLOAD_FOLDER` exists (defaults to `uploads/`).

Suggested environment variables if you refactor:

- SECRET_KEY
- ADMIN_USERNAME, ADMIN_PASSWORD
- STRIPE_PUBLIC_KEY, STRIPE_SECRET_KEY, STRIPE_PRICE_ID, STRIPE_WEBHOOK_SECRET
- MAIL_SERVER, MAIL_PORT, MAIL_USE_TLS, MAIL_USERNAME, MAIL_PASSWORD, MAIL_DEFAULT_SENDER
- BASE_URL, UPLOAD_FOLDER

4) Run the app

```bash
python app.py
```

By default it starts on http://localhost:5000.

### Running tests

```bash
python -m unittest -v unit_tests.py
```

You can also run with pytest if you prefer, but the provided tests use `unittest`.

## Key routes (API and pages)

- GET `/` — Home page
- POST `/get_dojos` — Search by city (form field: `location`); returns dojo list partial
- POST `/get_near_me` — Nearby dojos (form fields: `latitude`, `longitude`); returns dojo list partial
- GET `/dojo_details?dojo_id=<id>` — Dojo details + schedules
- GET `/premium_dojo_form` — Premium listing form (requires login)
- POST `/add_dojo_to_premium` — Starts Stripe Checkout subscription with submitted dojo data and schedules
- GET `/signup` — Signup page
- POST `/signup_form` — Create user (json response with `redirect`)
- GET `/login` — Login page
- POST `/login_form` — Login by email or username (json response with `redirect`)
- GET `/manage_dojos` — Manage the current user’s dojos (requires login)
- GET `/edit_dojo/<int:dojo_id>` — Edit dojo page
- POST `/edit_dojo/<int:dojo_id>` — Update dojo details and schedules
- GET `/admin_login` — Admin login page
- POST `/admin_login_form` — Admin login (json response with `redirect`)
- GET `/admin_dashboard` — Admin dashboard (requires admin session)
- GET `/uploads/<filename>` — Serve uploaded images
- GET `/success` — Stripe success page
- GET `/cancel` — Stripe cancel page
- POST `/webhook` — Stripe webhook endpoint

## Database schema (summary)

Tables created by `DB/set_up_database.py`:

- `users(id, username UNIQUE, email UNIQUE, password, created_at)`
- `dojos(id, name, address, city, website, phone, email, sensei_path, image_path, price_per_month, head_instructor, latitude, longitude, user_id, valid_subscription)`
- `schedules(id, dojo_id, day_of_week, start_time, end_time, instructor, competition_only, age_range)`

`dojos.user_id` references `users.id` (ON DELETE CASCADE). `schedules.dojo_id` references `dojos.id` (ON DELETE CASCADE).

## Payments and webhooks

- Purchases are handled via Stripe Checkout subscriptions.
- On `checkout.session.completed`, the app:
  - Persists a dojo record (and schedules) using the metadata captured before checkout
  - Geocodes the address and stores `latitude`/`longitude`
  - Sends an email notification to the project inbox

Local webhook testing (optional):

```bash
# In one terminal: run the app on http://localhost:5000
python app.py

# In another terminal: forward Stripe events to your local webhook
# Requires Stripe CLI and a webhook secret set in app.py
stripe listen --forward-to localhost:5000/webhook
```

Ensure `BASE_URL` points to your local app when testing.

## Email configuration

Flask-Mail is configured to use SMTP (Gmail in the sample). If you test with Gmail:

- Enable 2FA and create an App Password
- Use that App Password as `MAIL_PASSWORD`
- Consider rate limits and provider policies

## File uploads

- Images posted in forms are saved under `uploads/`
- The app serves them from `/uploads/<filename>`
- Ensure `uploads/` is writable in your environment

## Security and production readiness

- Do NOT commit secrets to source control; use environment variables or a secret manager
- Replace the demo keys/passwords in `app.py`
- Use secure cookies and CSRF protection for forms
- Validate/sanitize uploaded files; restrict content types and size
- Set a unique Nominatim user-agent and respect usage policies
- Consider gunicorn/uwsgi for deployment behind a reverse proxy
- Configure HTTPS (especially for Stripe redirects and webhooks)
- Set proper logging and error handling

## Troubleshooting

- Near-me results empty: ensure dojos have valid `latitude/longitude` (created on payment via geocoding) and you submit realistic coordinates
- Webhook not firing: check Stripe CLI forwarding, signature secret, and that your endpoint is reachable
- Emails not sending: verify SMTP credentials, ports, and app password
- DB errors: delete and recreate `DB/dojo_listings.db` using `DB/set_up_database.py`

## Contributing

1. Fork the repo and create a feature branch
2. Make changes with tests where applicable
3. Open a Pull Request with a clear description and screenshots if UI changes

## License

No license file is provided. If you intend to open source this project, consider adding a LICENSE (e.g., MIT, Apache-2.0, GPL).
