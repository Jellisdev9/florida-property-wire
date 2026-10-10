import datetime

from django.core.management.base import BaseCommand

from articles.models import Article

SEED_SOURCE_NAME = "seed-script"

ARTICLES = [
    dict(
        slug="seed-article-boca-raton-record-sale",
        title="Boca Raton Waterfront Estate Sets Record",
        headline="Boca Raton waterfront estate sells for $32.5M, a record for the block",
        subheadline="The seven-bedroom estate closed after three weeks on the market.",
        category=Article.Category.NOTABLE_SALE,
        body="This is placeholder seed content confirming the deploy pipeline renders real articles end to end.",
        byline="Staff Writer",
        published_date=datetime.date.today(),
        is_featured=True,
    ),
    dict(
        slug="seed-article-top-agent-profile",
        title="Miami Beach Team Tops Monthly Rankings",
        headline="The Jills Zeder Group leads South Florida agents again this month",
        category=Article.Category.AGENT_WATCH,
        body="This is placeholder seed content confirming the deploy pipeline renders real articles end to end.",
        byline="Staff Writer",
        published_date=datetime.date.today(),
    ),
    dict(
        slug="seed-article-brickell-inventory",
        title="Brickell Condo Inventory Tightens",
        headline="Brickell condo towers sell out as inventory tightens",
        category=Article.Category.NEIGHBORHOOD_WATCH,
        body="This is placeholder seed content confirming the deploy pipeline renders real articles end to end.",
        byline="Staff Writer",
        published_date=datetime.date.today(),
    ),
    dict(
        slug="seed-article-orlando-development",
        title="New Mixed-Use Tower Breaks Ground in Orlando",
        headline="Developer breaks ground on new downtown Orlando mixed-use tower",
        category=Article.Category.DEVELOPMENT,
        body="This is placeholder seed content confirming the deploy pipeline renders real articles end to end.",
        byline="Staff Writer",
        published_date=datetime.date.today(),
    ),
    dict(
        slug="seed-article-statewide-market-pulse",
        title="Florida Median Prices Mixed in Latest Reading",
        headline="Florida median home prices rise in Tampa, cool in Orlando",
        category=Article.Category.MARKET_PULSE,
        body="This is placeholder seed content confirming the deploy pipeline renders real articles end to end.",
        byline="Staff Writer",
        published_date=datetime.date.today(),
    ),
]


class Command(BaseCommand):
    help = "Seeds placeholder Article rows (one per category, one featured) for manual QA before the real content pipeline exists."

    def handle(self, *args, **options):
        created_count = 0
        for article in ARTICLES:
            _, created = Article.objects.get_or_create(
                slug=article["slug"],
                defaults={**article, "source_name": SEED_SOURCE_NAME},
            )
            created_count += created

        self.stdout.write(
            f"Article: {created_count} created, {len(ARTICLES) - created_count} already existed."
        )
