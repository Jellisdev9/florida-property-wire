#!/usr/bin/env bash
# One-time (and safe-to-rerun) local dev environment setup. Replaces the
# README's manual step-by-step: copies the two .env templates and the
# Compose override template (skips any that already exist — never
# overwrites real local secrets/config), starts Docker's db container,
# installs backend deps, runs migrations, and seeds placeholder demo
# content so the site actually has something to look at.
#
# Usage (from anywhere in the repo): scripts/setup_dev_env.sh
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

copy_if_missing() {
	local src="$1" dest="$2"
	if [ -f "$dest" ]; then
		echo "Skipping $dest (already exists)"
	else
		cp "$src" "$dest"
		echo "Created $dest from $src"
	fi
}

echo "== 1/6: env files and Compose override =="
copy_if_missing .env.example .env
copy_if_missing backend/.env.example backend/.env
copy_if_missing docker-compose.override.yml.example docker-compose.override.yml

echo "== 2/6: starting Docker's db container =="
docker compose up -d db

echo "== 3/6: waiting for Postgres to report healthy =="
until [ "$(docker compose ps db --format '{{.Health}}')" = "healthy" ]; do
	sleep 1
done

echo "== 4/6: installing backend dependencies (uv sync) =="
(cd backend && uv sync)

echo "== 5/6: running migrations =="
(cd backend && uv run python manage.py migrate)

echo "== 6/6: seeding placeholder demo content (idempotent, safe to rerun) =="
(cd backend && uv run python manage.py seed_market_demo_data)
(cd backend && uv run python manage.py seed_sales_demo_data)
(cd backend && uv run python manage.py seed_articles_demo_data)

cat <<'EOF'

Done. Next steps:
  cd backend && uv run python manage.py createsuperuser   # one-time, for /admin
  cd backend && ./tailwindcss -i static/css/input.css -o static/css/output.css --watch
  cd backend && uv run python manage.py runserver 8000

Or verify against the full production-equivalent stack instead of runserver:
  docker compose up --build
EOF
