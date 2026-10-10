from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from articles.models import Article
from market.models import Agent, FastestGrowingMarket, MarketMetric, NeighborhoodIntel
from sales.models import NotableSale


class SeedMarketDemoDataCommandTest(TestCase):
    def test_creates_five_market_metrics(self):
        call_command("seed_market_demo_data", stdout=StringIO())
        self.assertEqual(MarketMetric.objects.count(), 5)

    def test_market_metrics_are_tagged_as_seed_data(self):
        call_command("seed_market_demo_data", stdout=StringIO())
        self.assertEqual(
            MarketMetric.objects.filter(source_name="seed-script").count(), 5
        )

    def test_creates_five_agents_for_the_current_period(self):
        call_command("seed_market_demo_data", stdout=StringIO())
        now = timezone.now()
        agents = Agent.objects.filter(period_month=now.month, period_year=now.year)
        self.assertEqual(agents.count(), 5)
        self.assertEqual(sorted(agents.values_list("rank", flat=True)), [1, 2, 3, 4, 5])

    def test_creates_at_least_three_neighborhoods_with_mixed_tags(self):
        call_command("seed_market_demo_data", stdout=StringIO())
        self.assertGreaterEqual(NeighborhoodIntel.objects.count(), 3)
        self.assertGreater(
            NeighborhoodIntel.objects.values_list("tag", flat=True).distinct().count(), 1
        )

    def test_creates_five_fastest_growing_markets_for_the_current_period(self):
        call_command("seed_market_demo_data", stdout=StringIO())
        now = timezone.now()
        rows = FastestGrowingMarket.objects.filter(period_month=now.month, period_year=now.year)
        self.assertEqual(rows.count(), 5)
        self.assertEqual(sorted(rows.values_list("rank", flat=True)), [1, 2, 3, 4, 5])

    def test_running_twice_does_not_duplicate_rows(self):
        call_command("seed_market_demo_data", stdout=StringIO())
        call_command("seed_market_demo_data", stdout=StringIO())
        now = timezone.now()
        self.assertEqual(MarketMetric.objects.count(), 5)
        self.assertEqual(
            Agent.objects.filter(period_month=now.month, period_year=now.year).count(), 5
        )
        self.assertEqual(NeighborhoodIntel.objects.count(), 4)
        self.assertEqual(
            FastestGrowingMarket.objects.filter(
                period_month=now.month, period_year=now.year
            ).count(),
            5,
        )


class RemoveSeedDataCommandTest(TestCase):
    def test_removes_seed_rows_across_every_app_and_leaves_real_rows_alone(self):
        call_command("seed_market_demo_data", stdout=StringIO())
        call_command("seed_sales_demo_data", stdout=StringIO())
        call_command("seed_articles_demo_data", stdout=StringIO())

        real_metric = MarketMetric.objects.create(
            city="Naples", metric_label="Median Price", value_display="$720,000",
            change_display="+1.0%", source_name="Zillow",
        )
        real_sale = NotableSale.objects.create(
            slug="real-sale", title="Real Sale", price=1_000_000,
            location="1 Real St, Naples, FL", city="Naples",
            region=NotableSale.Region.SOUTH_FLORIDA,
            property_type=NotableSale.PropertyType.SINGLE_FAMILY,
            close_date="2026-01-01", source_name="MLS",
        )
        real_article = Article.objects.create(
            slug="real-article", title="Real Article", headline="Real Headline",
            category=Article.Category.MARKET_PULSE, body="Real body.",
            byline="Real Byline", published_date="2026-01-01", source_name="Staff",
        )

        call_command("remove_seed_data", stdout=StringIO())

        self.assertEqual(MarketMetric.objects.filter(source_name="seed-script").count(), 0)
        self.assertEqual(Agent.objects.filter(source_name="seed-script").count(), 0)
        self.assertEqual(NeighborhoodIntel.objects.filter(source_name="seed-script").count(), 0)
        self.assertEqual(
            FastestGrowingMarket.objects.filter(source_name="seed-script").count(), 0
        )
        self.assertEqual(NotableSale.objects.filter(source_name="seed-script").count(), 0)
        self.assertEqual(Article.objects.filter(source_name="seed-script").count(), 0)

        self.assertTrue(MarketMetric.objects.filter(pk=real_metric.pk).exists())
        self.assertTrue(NotableSale.objects.filter(pk=real_sale.pk).exists())
        self.assertTrue(Article.objects.filter(pk=real_article.pk).exists())
