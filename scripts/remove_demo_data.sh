#!/usr/bin/env bash
# Deletes every row created by scripts/seed_demo_data.sh (anything tagged
# source_name="seed-script" across MarketMetric, Agent, NeighborhoodIntel,
# FastestGrowingMarket, NotableSale, and Article), leaving real content
# untouched. Run once the automated content pipeline is live and demo
# content is no longer needed.
#
# Usage (on the VPS, from the repo root): scripts/remove_demo_data.sh
set -euo pipefail

docker exec -i florida-property-wire-web python manage.py remove_seed_data
