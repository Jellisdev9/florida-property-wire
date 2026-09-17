# Florida Property Wire

Editorial/business-news style real estate publication focused on Florida real estate.
Covers notable sales, agent moves, market trends, neighborhoods, luxury closings, and development news.

## Architecture

**One server. No Node. No React to run the site.** Django renders HTML server-side.

- **Backend** — Django + Django REST Framework (`backend/`)
- **Templates** — Django templates (`backend/templates/`), styled with Tailwind CSS (standalone CLI binary, no Node build step)
- **Database** — PostgreSQL (production) / SQLite (development)
- The DRF `/api/` endpoints are kept alongside the template views (useful for mobile/RSS/future use) but the site itself does not consume them — views query the ORM directly and pass context to templates.
- The original React SPA (`artifacts/florida-property-review/`) has been removed. The project pivoted from React+API to Django server-rendered templates; see git history before this deletion if the old React code is ever needed.

## Tech Stack

### Backend
- Django 5.x + Django REST Framework
- django-cors-headers, django-filter
- PostgreSQL (prod) / SQLite (dev)
- python-dotenv
- Tailwind CSS via the standalone CLI binary (`backend/tailwindcss`, gitignored — re-download command below)

### Deployment
- Docker Compose: `web` (gunicorn), `db` (Postgres), `caddy` (reverse proxy + TLS), `backup` (nightly Postgres backups)
- Caddy — automatic TLS (internal CA locally, Let's Encrypt in production) from one `Caddyfile`
- GitHub Actions — test gate + image build/push to GHCR (`.github/workflows/ci.yml`)

## Project Structure

```
florida-property-wire/
├── CLAUDE.md
├── backup/                         # nightly Postgres backup service (pg_dump + rclone)
│   ├── Dockerfile
│   └── backup.sh
├── backend/                        # Django project root
│   ├── manage.py
│   ├── pyproject.toml              # uv-managed deps
│   ├── .env.example
│   ├── fixtures/                   # seed data (JSON)
│   ├── tailwindcss                 # standalone Tailwind binary (gitignored)
│   ├── static/css/{input,output}.css
│   ├── templates/
│   │   ├── base.html               # master template — header, market strip, footer
│   │   ├── home.html
│   │   ├── article_detail.html
│   │   ├── notable_sales.html
│   │   └── partials/
│   │       ├── top_markets_sidebar.html
│   │       └── top_agents_sidebar.html
│   ├── backend/                    # Django config package
│   │   ├── settings/
│   │   │   ├── base.py             # shared settings
│   │   │   ├── development.py      # SQLite, DEBUG=True, CORS localhost
│   │   │   └── production.py       # PostgreSQL, DEBUG=False
│   │   ├── urls.py                 # root URL config (template pages + /api/)
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── articles/                   # article content app
│   ├── sales/                      # notable sales app
│   ├── market/                     # market metrics, agents, neighborhoods app
│   └── subscribers/                # newsletter signups app
```

## Django Apps

### articles/
Manages editorial article content.
- **Model:** `Article` — slug, title, headline, subheadline, category, body, byline, author_avatar_url, read_time_minutes, hero_image_url, published_date, is_featured, status, source_url, source_name
- **Status:** `DRAFT` / `PENDING_REVIEW` / `PUBLISHED` — an editorial workflow field, not a boolean. Only `status=PUBLISHED` articles are ever shown on the site. Default is `PUBLISHED` (matches prior `is_published` behavior for hand-written/admin-created articles); an automated content pipeline should explicitly set `PENDING_REVIEW` so nothing goes live without editor approval.
- **`source_url`/`source_name`:** attribution fields for auto-generated/scraped articles — blank for hand-written ones.
- **Categories:** NOTABLE_SALE, AGENT_WATCH, NEIGHBORHOOD_WATCH, DEVELOPMENT, MARKET_PULSE

### sales/
Manages notable property sales.
- **Model:** `NotableSale` — slug, title, price, location, city, region, property_type, close_date, hero_image_url, is_featured, article (FK), brokerage, beds, baths, sq_ft, status, source_url, source_name
- **Status/source:** same editorial-workflow pattern as `Article` (see above) — added because this model previously had **no publish gate at all** (every row was always shown), which is riskier than `Article`'s old boolean once sale records start arriving from an automated pipeline.
- **Regions:** SOUTH_FLORIDA, TAMPA_BAY, ORLANDO, JACKSONVILLE, PANHANDLE
- **Types:** WATERFRONT_ESTATE, CONDO_PENTHOUSE, CONDO_RESIDENCE, COMMERCIAL, SINGLE_FAMILY

### market/
Manages all market data widgets shown in the header strip and sidebars.
- **Model:** `MarketMetric` — powers the 5-tile header strip (city, value_display, change_display, is_positive)
- **Model:** `Agent` — top agents leaderboard (name, location, volume_display, rank, period_month/year)
- **Model:** `NeighborhoodIntel` — neighborhood watch cards (neighborhood, city, description, tag: HOT/RISING/COOLING)
- **Model:** `FastestGrowingMarket` — fastest growing markets sidebar (location, change_display, rank)
- All four models have `source_url`/`source_name` for attribution, same as `Article`/`NotableSale`. **No `status` field here on purpose** — these are short numeric widget values (ticker tiles, rankings), not long-form content, so the risk of a bad scraped number going live immediately is low and easily corrected. Revisit if that judgment call turns out wrong.
- **Known gap, not yet fixed:** `FastestGrowingMarket.rank` is globally unique with no period field, unlike `Agent` (`unique_together = [rank, period_month, period_year]`). Refreshing it periodically will hit a unique-constraint error unless old rows are deleted first, or it gets period fields added to match `Agent`.

### subscribers/
Manages newsletter subscriptions.
- **Model:** `Subscriber` — email, subscribed_at, is_active
- Handles duplicate email gracefully (redirects with no error instead of erroring)

## Pages (template-rendered)

| URL | Template | View | Notes |
|-----|----------|------|-------|
| `/` | `home.html` | `articles.views.home_view` | featured article hero, article cards, sidebars |
| `/articles/<slug>/` | `article_detail.html` | `articles.views.article_detail_view` | 404 on unknown slug |
| `/notable-sales/` | `notable_sales.html` | `sales.views.notable_sales_view` | region filter via `?region=`, statewide "Top Luxury Closings" sidebar ignores the filter by design |
| `/subscribe/` | — (redirect only) | `subscribers.views.subscribe_view` | POST-only, redirects back to `next` |

## API Endpoints (kept, not used by the site itself)

All endpoints are prefixed with `/api/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/articles/ | List articles (`?category=`) |
| GET | /api/articles/featured/ | Featured article |
| GET | /api/articles/`<slug>`/ | Article detail |
| GET | /api/sales/ | List notable sales (`?region=`) |
| GET | /api/sales/featured/ | Featured sale |
| GET | /api/sales/top-closings/ | Top 5 closings by price |
| GET | /api/market/metrics/ | 5-tile header strip data |
| GET | /api/market/neighborhoods/ | Neighborhood intel cards |
| GET | /api/market/fastest-growing/ | Fastest growing markets |
| GET | /api/agents/top/ | Top agents this month |
| POST | /api/subscribers/ | Subscribe to newsletter |

## Development Workflow

Uses [uv](https://docs.astral.sh/uv/) for Python dependency management. Dependencies live in `backend/pyproject.toml`. No Node/pnpm needed to run the site.

```bash
# Backend setup (run once)
cd backend
cp .env.example .env
uv sync                              # creates .venv and installs all deps
uv run python manage.py migrate
uv run python manage.py createsuperuser

# Seed mock data (after migrations)
uv run python manage.py loaddata fixtures/initial_data.json

# Tailwind CSS — standalone binary, no Node required
curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-linux-x64
chmod +x tailwindcss-linux-x64
mv tailwindcss-linux-x64 tailwindcss
./tailwindcss -i static/css/input.css -o static/css/output.css
# add --watch during active development to recompile on template changes

# Run
uv run python manage.py runserver 8000

# Run tests
uv run python manage.py test         # all apps
uv run python manage.py test articles # single app

# Add a dependency
uv add <package>
```

Before pushing, verify against the same stack that runs in production:

```bash
docker compose up --build   # from the repo root — web + Postgres + Caddy
```

`manage.py` defaults `DJANGO_SETTINGS_MODULE` to `backend.settings.development`, and `development.py` hardcodes SQLite with no required secrets — the server runs even without a `.env` file present, though one should still be created for `SECRET_KEY` and other overrides.

## Environment Variables

See `backend/.env.example`. Key variables:
- `DJANGO_SETTINGS_MODULE` — `backend.settings.development` locally
- `SECRET_KEY` — required in production
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` — production PostgreSQL
- `CORS_ALLOWED_ORIGINS` — comma-separated list of allowed frontend origins (relevant only for `/api/` consumers)

## Testing — TDD Red/Green

This project follows strict TDD. Every feature is written test-first: write a failing test (red), write the minimum code to make it pass (green), then refactor.

```bash
cd backend
uv run python manage.py test          # run all tests
uv run python manage.py test articles # run one app
```

Test file location mirrors the app structure:

```
backend/
├── articles/tests/{test_models,test_views,test_template_views}.py
├── sales/tests/{test_models,test_views,test_template_views}.py
├── market/tests/{test_models,test_views}.py
└── subscribers/tests/{test_models,test_views,test_template_views}.py
```

Use Django's built-in `TestCase` + DRF's `APITestCase`. `test_template_views.py` files use `self.client.get()`/`self.assertTemplateUsed`/`self.assertContains` for page-level tests, and `response.context[...]` when an assertion needs to target a specific context variable (e.g. the sales grid queryset) rather than scraping rendered HTML — this matters when a page has both a filtered section (the grid) and an unfiltered one (a statewide sidebar widget).

Cycle for every endpoint, model, or view change:
1. **Red** — write the test, assert the exact response shape/status/context, run it and watch it fail
2. **Green** — write the minimum model/view code to pass
3. **Refactor** — clean up, keep tests green

### What to test

| Layer | Test focus |
|-------|-----------|
| Models | field validation, `__str__`, unique constraints, ordering, computed properties (e.g. `price_display`) |
| Views (template) | status codes, template used, context contents, rendered content, filter params (`?region=`, `?category=`), edge cases (404, duplicate subscriber) |
| Views (API) | status codes, response shape, filter params, edge cases |

### What not to test

- Django internals (ORM, admin)
- Third-party library behavior
- Trivial getters with no logic

## Deployment strategy

Local → CI test gate → manual-triggered deploy, no persistent staging
environment (solo project, no team to coordinate, no
payments/compliance exposure — revisit if any of that changes). CI
(GitHub Actions, `.github/workflows/ci.yml`) is what replaces the
safety a staging environment would give: every push/PR to `main` runs
the full test suite against a real Postgres service container.

This project is one of several (~20 apps planned over a short window)
meant to share **one VPS** rather than each getting its own — at this
traffic level, per-app instances would mean paying for isolation none
of them need yet. Each app is containerized identically: a
`Dockerfile` + `docker-compose.yml` (Django/gunicorn + Postgres +
Caddy) that runs unchanged on the dev machine and on the VPS. Caddy
replaces nginx+`mkcert`: it auto-detects `localhost`/an IP vs. a real
domain and switches between its internal self-signed CA and real
Let's Encrypt automatically, from the same `Caddyfile`, via one
`SITE_ADDRESS` env var — no separate local-TLS tooling needed.

Caddy is currently bundled per-app (this repo's own `docker-compose.yml`
runs its own Caddy on 80/443), **not** yet extracted into shared
multi-app infra — that refactor is deliberately deferred until a
second app actually needs to share the VPS's ports 80/443, not built
speculatively now.

On every push to `main`, CI runs tests and — if green — builds the
Docker image and pushes it to GHCR
(`ghcr.io/<owner>/florida-property-wire`). Actually rolling that
image out to the VPS is a separate, manually-triggered step
(`workflow_dispatch` in the same workflow, SSHes in and runs
`docker compose pull && docker compose up -d`) rather than
auto-deploying on every push — kept manual until the pipeline is
proven.

Local dev (`manage.py runserver` + SQLite) is unchanged for the fast
iteration loop. `docker compose up --build` (the same stack that runs
on the VPS) is the final pre-ship verification step, run before
pushing.

### Postgres backups

A `backup` service (`backup/Dockerfile`, `backup/backup.sh`) runs
`pg_dump | gzip` on a loop (default every 24h, `BACKUP_INTERVAL_SECONDS`)
and pushes each dump offsite via `rclone`, to any S3-compatible bucket
(AWS S3, Backblaze B2, Cloudflare R2, MinIO, ...) — see `.env.example`
for the `RCLONE_CONFIG_REMOTE_*` vars. Deliberately **not** the
pre-built `postgres-backup-s3`-style Docker Hub images: the popular
ones (`schickling/postgres-backup-s3` and its most-starred fork) are
archived/unmaintained, and the actively-maintained alternative
(`prodrigestivill/postgres-backup-local`) only writes to local disk —
which defeats the point, since losing the VPS disk would take the DB
and its backups together. A ~20-line custom script matches this
project's existing bias toward owning simple infra directly (same
reasoning as Caddy replacing nginx+`mkcert`) over depending on a
third-party image that might go stale.

Retention is handled by a lifecycle rule on the bucket itself (e.g.
expire objects after 30 days) rather than in app code — every
S3-compatible provider supports this natively, so there's no rotation
logic to write or test.

If `BACKUP_BUCKET` is unset, the container logs and skips each cycle
instead of failing — local dev and any environment without a bucket
configured yet just runs without backups, no crash loop.

**Verified locally**: `pg_dump` connects to the `db` service and
produces a valid gzip dump; `rclone copy` correctly delivers it to a
remote (tested against a local-filesystem `rclone` remote standing in
for real S3 credentials, which don't exist yet — see Next Steps).

## Next Steps

- [ ] Provision the shared VPS — decided: OVH VPS-2 (8GB RAM)
- [ ] Add `VPS_HOST` / `VPS_USER` / `VPS_SSH_KEY` repo secrets once
      the VPS exists, so the `deploy` job in
      `.github/workflows/ci.yml` can actually run
- [ ] Create a real S3-compatible bucket + credentials (any provider)
      and set `BACKUP_BUCKET` / `RCLONE_CONFIG_REMOTE_*` in production's
      `.env`, plus a lifecycle rule on the bucket for retention — the
      `backup` service is built and verified but has never pushed to a
      real remote yet
- [ ] First real deploy: `git clone` this repo onto the VPS at
      `/opt/florida-property-wire`, set `SITE_ADDRESS` to the real
      domain in its root `.env`, `docker compose up -d`
