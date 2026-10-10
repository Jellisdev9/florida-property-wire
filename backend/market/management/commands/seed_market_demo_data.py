from django.core.management.base import BaseCommand
from django.utils import timezone

from market.models import Agent, FastestGrowingMarket, MarketMetric, NeighborhoodIntel

SEED_SOURCE_NAME = "seed-script"

MARKET_METRICS = [
    dict(city="Miami", metric_label="Median Price", value_display="$685,000", change_display="+6.2%", is_positive=True, sort_order=0),
    dict(city="Tampa", metric_label="Median Price", value_display="$412,000", change_display="+3.1%", is_positive=True, sort_order=1),
    dict(city="Orlando", metric_label="Median Price", value_display="$398,500", change_display="-1.4%", is_positive=False, sort_order=2),
    dict(city="Jacksonville", metric_label="Median Price", value_display="$349,900", change_display="+2.8%", is_positive=True, sort_order=3),
    dict(city="Fort Walton Beach", metric_label="Median Price", value_display="$455,000", change_display="+0.6%", is_positive=True, sort_order=4),
]

AGENTS = [
    dict(name="The Jills Zeder Group", location="Miami Beach", volume_display="$98.4M", rank=1),
    dict(name="Dina Goldentayer", location="Miami", volume_display="$86.1M", rank=2),
    dict(name="Jonathan Fryd", location="Tampa", volume_display="$71.9M", rank=3),
    dict(name="Stewart Wade", location="Orlando", volume_display="$64.3M", rank=4),
    dict(name="Christie Osborne", location="Jacksonville", volume_display="$58.7M", rank=5),
]

NEIGHBORHOODS = [
    dict(neighborhood="Brickell", city="Miami", description="Condo inventory tightens as towers sell out.", tag=NeighborhoodIntel.Tag.HOT, sort_order=0),
    dict(neighborhood="Winter Park", city="Orlando", description="Steady demand, low days-on-market.", tag=NeighborhoodIntel.Tag.STABLE, sort_order=1),
    dict(neighborhood="Riverside", city="Jacksonville", description="New listings up, buyers gaining leverage.", tag=NeighborhoodIntel.Tag.COOLING, sort_order=2),
    dict(neighborhood="Hyde Park", city="Tampa", description="Multiple-offer situations returning.", tag=NeighborhoodIntel.Tag.RISING, sort_order=3),
]

FASTEST_GROWING_MARKETS = [
    dict(location="Sarasota", change_display="+13.5%", rank=1),
    dict(location="Cape Coral", change_display="+11.2%", rank=2),
    dict(location="Lakeland", change_display="+9.8%", rank=3),
    dict(location="Ocala", change_display="+8.4%", rank=4),
    dict(location="Port St. Lucie", change_display="+7.1%", rank=5),
]


class Command(BaseCommand):
    help = "Seeds placeholder MarketMetric and Agent rows for manual QA before the real content pipeline exists."

    def handle(self, *args, **options):
        metrics_created = 0
        for metric in MARKET_METRICS:
            _, created = MarketMetric.objects.get_or_create(
                city=metric["city"],
                metric_label=metric["metric_label"],
                defaults={**metric, "source_name": SEED_SOURCE_NAME},
            )
            metrics_created += created

        now = timezone.now()
        agents_created = 0
        for agent in AGENTS:
            _, created = Agent.objects.get_or_create(
                rank=agent["rank"],
                period_month=now.month,
                period_year=now.year,
                defaults={
                    **agent,
                    "period_month": now.month,
                    "period_year": now.year,
                    "source_name": SEED_SOURCE_NAME,
                },
            )
            agents_created += created

        neighborhoods_created = 0
        for neighborhood in NEIGHBORHOODS:
            _, created = NeighborhoodIntel.objects.get_or_create(
                neighborhood=neighborhood["neighborhood"],
                city=neighborhood["city"],
                defaults={**neighborhood, "source_name": SEED_SOURCE_NAME},
            )
            neighborhoods_created += created

        fastest_growing_created = 0
        for market in FASTEST_GROWING_MARKETS:
            _, created = FastestGrowingMarket.objects.get_or_create(
                rank=market["rank"],
                period_month=now.month,
                period_year=now.year,
                defaults={
                    **market,
                    "period_month": now.month,
                    "period_year": now.year,
                    "source_name": SEED_SOURCE_NAME,
                },
            )
            fastest_growing_created += created

        self.stdout.write(
            f"MarketMetric: {metrics_created} created, {len(MARKET_METRICS) - metrics_created} already existed. "
            f"Agent: {agents_created} created, {len(AGENTS) - agents_created} already existed. "
            f"NeighborhoodIntel: {neighborhoods_created} created, {len(NEIGHBORHOODS) - neighborhoods_created} already existed. "
            f"FastestGrowingMarket: {fastest_growing_created} created, {len(FASTEST_GROWING_MARKETS) - fastest_growing_created} already existed."
        )
