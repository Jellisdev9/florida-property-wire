#!/usr/bin/env bash
# Seeds placeholder demo content (MarketMetric, Agent, NeighborhoodIntel,
# FastestGrowingMarket, NotableSale, Article) via three Django management
# commands, run inside the live web container. Covers every public page
# for manual QA before the real content pipeline exists. Idempotent — each
# command uses get_or_create, safe to rerun.
#
# Usage (on the VPS, from the repo root): scripts/seed_demo_data.sh
set -euo pipefail

for command in seed_market_demo_data seed_sales_demo_data seed_articles_demo_data; do
	docker exec -i florida-property-wire-web python manage.py "${command}"
done
