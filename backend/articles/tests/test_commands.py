from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from articles.models import Article


class SeedArticlesDemoDataCommandTest(TestCase):
    def test_creates_one_article_per_category(self):
        call_command("seed_articles_demo_data", stdout=StringIO())
        categories_seeded = set(Article.objects.values_list("category", flat=True))
        self.assertEqual(categories_seeded, set(Article.Category.values))

    def test_exactly_one_article_is_featured(self):
        call_command("seed_articles_demo_data", stdout=StringIO())
        self.assertEqual(Article.objects.filter(is_featured=True).count(), 1)

    def test_articles_are_published_and_tagged_as_seed_data(self):
        call_command("seed_articles_demo_data", stdout=StringIO())
        seeded = Article.objects.filter(source_name="seed-script")
        self.assertEqual(seeded.count(), Article.objects.count())
        self.assertTrue(all(a.status == Article.Status.PUBLISHED for a in seeded))

    def test_running_twice_does_not_duplicate_rows(self):
        call_command("seed_articles_demo_data", stdout=StringIO())
        count_after_first_run = Article.objects.count()
        call_command("seed_articles_demo_data", stdout=StringIO())
        self.assertEqual(Article.objects.count(), count_after_first_run)
