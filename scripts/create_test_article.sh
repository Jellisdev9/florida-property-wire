#!/usr/bin/env bash
# Creates (or confirms) one test Article via the running web container's
# Django shell — for confirming the deploy pipeline renders real content
# end to end. Idempotent: reruns with the same slug just report it already
# exists instead of erroring.
#
# Usage (on the VPS, from anywhere): scripts/create_test_article.sh [slug]
set -euo pipefail

SLUG="${1:-test-article}"

docker exec -i florida-property-wire-web python manage.py shell <<PYEOF
from articles.models import Article
from datetime import date

article, created = Article.objects.get_or_create(
    slug="${SLUG}",
    defaults=dict(
        title="Test Article",
        headline="Confirming the site renders content end to end",
        category=Article.Category.MARKET_PULSE,
        body="This is a test article confirming the deploy pipeline works.",
        byline="Staff Writer",
        published_date=date.today(),
    ),
)
print(("Created" if created else "Already exists") + ":", article.headline)
PYEOF
