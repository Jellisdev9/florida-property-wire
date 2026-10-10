from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from sales.models import NotableSale


class SeedSalesDemoDataCommandTest(TestCase):
    def test_creates_one_sale_per_region(self):
        call_command("seed_sales_demo_data", stdout=StringIO())
        regions_seeded = set(NotableSale.objects.values_list("region", flat=True))
        self.assertEqual(regions_seeded, set(NotableSale.Region.values))

    def test_exactly_one_sale_is_featured(self):
        call_command("seed_sales_demo_data", stdout=StringIO())
        self.assertEqual(NotableSale.objects.filter(is_featured=True).count(), 1)

    def test_sales_are_tagged_as_seed_data(self):
        call_command("seed_sales_demo_data", stdout=StringIO())
        self.assertEqual(
            NotableSale.objects.filter(source_name="seed-script").count(),
            NotableSale.objects.count(),
        )

    def test_running_twice_does_not_duplicate_rows(self):
        call_command("seed_sales_demo_data", stdout=StringIO())
        count_after_first_run = NotableSale.objects.count()
        call_command("seed_sales_demo_data", stdout=StringIO())
        self.assertEqual(NotableSale.objects.count(), count_after_first_run)
