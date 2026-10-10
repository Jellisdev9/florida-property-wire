from django.core.management.base import BaseCommand

from articles.models import Article
from market.models import Agent, FastestGrowingMarket, MarketMetric, NeighborhoodIntel
from sales.models import NotableSale

SEED_SOURCE_NAME = "seed-script"

SEEDED_MODELS = [
    MarketMetric,
    Agent,
    NeighborhoodIntel,
    FastestGrowingMarket,
    NotableSale,
    Article,
]


class Command(BaseCommand):
    help = "Deletes every row created by the seed_*_demo_data commands (source_name='seed-script'), leaving real content untouched."

    def handle(self, *args, **options):
        for model in SEEDED_MODELS:
            deleted_count, _ = model.objects.filter(source_name=SEED_SOURCE_NAME).delete()
            self.stdout.write(f"{model.__name__}: {deleted_count} deleted.")
