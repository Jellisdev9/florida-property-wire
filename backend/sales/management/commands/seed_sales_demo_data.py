import datetime

from django.core.management.base import BaseCommand

from sales.models import NotableSale

SEED_SOURCE_NAME = "seed-script"

SALES = [
    dict(
        slug="seed-sale-boca-raton-estate",
        title="Boca Raton Waterfront Estate",
        price=32_500_000,
        location="2100 Spanish River Rd, Boca Raton, FL",
        city="Boca Raton",
        region=NotableSale.Region.SOUTH_FLORIDA,
        property_type=NotableSale.PropertyType.WATERFRONT_ESTATE,
        close_date=datetime.date.today(),
        is_featured=True,
        brokerage="Compass Florida",
        beds=7,
        baths=9.5,
        sq_ft=14200,
    ),
    dict(
        slug="seed-sale-tampa-penthouse",
        title="Tampa Bay Skyline Penthouse",
        price=6_250_000,
        location="100 Bayshore Blvd, Tampa, FL",
        city="Tampa",
        region=NotableSale.Region.TAMPA_BAY,
        property_type=NotableSale.PropertyType.CONDO_PENTHOUSE,
        close_date=datetime.date.today(),
        brokerage="Smith & Associates",
        beds=3,
        baths=3.5,
        sq_ft=3800,
    ),
    dict(
        slug="seed-sale-orlando-single-family",
        title="Winter Park Lakefront Home",
        price=2_100_000,
        location="455 Lake Osceola Dr, Winter Park, FL",
        city="Winter Park",
        region=NotableSale.Region.ORLANDO,
        property_type=NotableSale.PropertyType.SINGLE_FAMILY,
        close_date=datetime.date.today(),
        brokerage="Fannie Hillman + Associates",
        beds=5,
        baths=4,
        sq_ft=5200,
    ),
    dict(
        slug="seed-sale-jacksonville-residence",
        title="Riverside Condo Residence",
        price=975_000,
        location="1431 Riverplace Blvd, Jacksonville, FL",
        city="Jacksonville",
        region=NotableSale.Region.JACKSONVILLE,
        property_type=NotableSale.PropertyType.CONDO_RESIDENCE,
        close_date=datetime.date.today(),
        brokerage="Berkshire Hathaway HomeServices",
        beds=2,
        baths=2,
        sq_ft=1650,
    ),
    dict(
        slug="seed-sale-panhandle-commercial",
        title="Destin Harbor Commercial Building",
        price=4_800_000,
        location="660 Harbor Blvd, Destin, FL",
        city="Destin",
        region=NotableSale.Region.PANHANDLE,
        property_type=NotableSale.PropertyType.COMMERCIAL,
        close_date=datetime.date.today(),
        brokerage="EXP Realty",
    ),
]


class Command(BaseCommand):
    help = "Seeds placeholder NotableSale rows (one per region, one featured) for manual QA before the real content pipeline exists."

    def handle(self, *args, **options):
        created_count = 0
        for sale in SALES:
            _, created = NotableSale.objects.get_or_create(
                slug=sale["slug"],
                defaults={**sale, "source_name": SEED_SOURCE_NAME},
            )
            created_count += created

        self.stdout.write(
            f"NotableSale: {created_count} created, {len(SALES) - created_count} already existed."
        )
