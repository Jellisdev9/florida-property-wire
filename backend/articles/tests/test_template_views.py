"""
Template view tests — one test class per view.

Pattern: each test class has a setUp() that creates the minimum DB objects
needed, then tests check status codes, correct templates, context variables,
and that key text actually appears in the rendered HTML.
"""
from django.test import TestCase
from django.urls import reverse
from articles.models import Article
import datetime


# ── Helpers ──────────────────────────────────────────────────────────────────

def make_article(**kwargs):
    """
    Factory for Article objects. Provides sensible defaults so individual
    tests only need to override the fields they care about.
    """
    defaults = {
        "slug": "test-article",
        "title": "Test Article",
        "headline": "Test Headline",
        "subheadline": "Test subheadline",
        "category": Article.Category.MARKET_PULSE,
        "body": "Body text.",
        "byline": "Staff Writer",
        "published_date": datetime.date.today(),
        "is_featured": False,
        "status": Article.Status.PUBLISHED,
    }
    defaults.update(kwargs)
    return Article.objects.create(**defaults)


# ── Step 4: base template loads ───────────────────────────────────────────────

class BaseTemplateTest(TestCase):
    """
    The home URL must use base.html as its parent template.
    This is the first minimal test — just proves the URL exists and
    the template inheritance chain is wired up.
    """

    def test_home_uses_base_template(self):
        # reverse('home') looks up the URL named 'home' in urls.py
        response = self.client.get(reverse("home"))
        # assertTemplateUsed checks that the named template was rendered
        self.assertTemplateUsed(response, "base.html")


# ── Step 5: home page ─────────────────────────────────────────────────────────

class HomeViewTest(TestCase):
    """
    Tests for the home page view. Creates a featured article so the
    view has something to show in the hero section.
    """

    def setUp(self):
        # setUp() runs before every test in this class — creates fresh DB objects
        self.featured = make_article(
            slug="featured-article",
            headline="Featured Headline",
            is_featured=True,
        )

    def test_returns_200(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        response = self.client.get(reverse("home"))
        # home.html should extend base.html — both should be reported as used
        self.assertTemplateUsed(response, "home.html")
        self.assertTemplateUsed(response, "base.html")

    def test_featured_article_in_context(self):
        # The view must pass 'featured' to the template context
        response = self.client.get(reverse("home"))
        self.assertIsNotNone(response.context["featured"])

    def test_featured_headline_renders(self):
        # The featured article's headline must appear somewhere in the HTML
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Featured Headline")

    def test_articles_in_context(self):
        # The view must pass an 'articles' list for the card row
        response = self.client.get(reverse("home"))
        self.assertIn("articles", response.context)


# ── Step 6: article detail page ───────────────────────────────────────────────

class ArticleDetailViewTest(TestCase):
    """
    Tests for /articles/<slug>/ — individual article page.
    """

    def setUp(self):
        self.article = make_article(
            slug="my-article",
            headline="My Article Headline",
            category=Article.Category.AGENT_WATCH,
        )

    def test_returns_200(self):
        # reverse('article_detail', args=['my-article']) → /articles/my-article/
        response = self.client.get(reverse("article_detail", args=["my-article"]))
        self.assertEqual(response.status_code, 200)

    def test_returns_404_for_missing_slug(self):
        response = self.client.get(reverse("article_detail", args=["does-not-exist"]))
        self.assertEqual(response.status_code, 404)

    def test_uses_correct_template(self):
        response = self.client.get(reverse("article_detail", args=["my-article"]))
        self.assertTemplateUsed(response, "article_detail.html")

    def test_headline_renders(self):
        response = self.client.get(reverse("article_detail", args=["my-article"]))
        self.assertContains(response, "My Article Headline")

    def test_article_in_context(self):
        response = self.client.get(reverse("article_detail", args=["my-article"]))
        self.assertEqual(response.context["article"], self.article)

    def test_links_to_sale_when_present(self):
        from sales.models import NotableSale
        article = make_article(slug="sale-story", headline="Sale Story", category=Article.Category.NOTABLE_SALE)
        NotableSale.objects.create(
            slug="linked-sale", title="Linked Sale", price=1000000, location="123 Main St",
            city="Miami", region=NotableSale.Region.SOUTH_FLORIDA,
            property_type=NotableSale.PropertyType.SINGLE_FAMILY,
            close_date=datetime.date.today(), article=article,
        )
        response = self.client.get(reverse("article_detail", args=["sale-story"]))
        self.assertContains(response, reverse("sale_detail", args=["linked-sale"]))

    def test_no_sale_link_when_absent(self):
        response = self.client.get(reverse("article_detail", args=["my-article"]))
        self.assertNotContains(response, "Sale Details")


# ── About page ─────────────────────────────────────────────────────────────────

class AboutViewTest(TestCase):
    """
    Tests for /about/ — the static masthead/about page.
    """

    def test_returns_200(self):
        response = self.client.get(reverse("about"))
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        response = self.client.get(reverse("about"))
        self.assertTemplateUsed(response, "about.html")
        self.assertTemplateUsed(response, "base.html")

    def test_contains_publication_name(self):
        response = self.client.get(reverse("about"))
        self.assertContains(response, "Florida Property Wire")


# ── Error pages ──────────────────────────────────────────────────────────────

class ErrorPagesTest(TestCase):
    """
    Tests for the custom 404/500 templates. DEBUG=False in test.py (see
    backend/settings/test.py), so Django's default error handlers
    (django.views.defaults.page_not_found / server_error) are active
    and resolve to these template names automatically — no view/URL
    wiring of our own to test.
    """

    def test_404_uses_custom_template(self):
        response = self.client.get("/this-page-does-not-exist/")
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")

    def test_404_page_content(self):
        response = self.client.get("/this-page-does-not-exist/")
        self.assertContains(response, "Page not found", status_code=404)

    def test_500_template_renders(self):
        # Not exercising Django's actual 500-dispatch machinery (that's
        # framework internals) — just confirming our own template is
        # valid and self-contained (no inheritance, no context needed).
        from django.template.loader import render_to_string
        rendered = render_to_string("500.html")
        self.assertIn("Something went wrong", rendered)


# ── Article archive ──────────────────────────────────────────────────────────

class ArticleArchiveViewTest(TestCase):
    """
    Tests for /articles/ — the paginated, all-categories article archive.
    """

    def test_returns_200(self):
        response = self.client.get(reverse("article_archive"))
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        response = self.client.get(reverse("article_archive"))
        self.assertTemplateUsed(response, "article_archive.html")
        self.assertTemplateUsed(response, "base.html")

    def test_development_category_article_shows(self):
        # DEVELOPMENT has no other dedicated page — this is the gap the
        # archive page exists to close.
        make_article(
            slug="development-article",
            headline="Development Headline",
            category=Article.Category.DEVELOPMENT,
        )
        response = self.client.get(reverse("article_archive"))
        self.assertContains(response, "Development Headline")

    def test_draft_articles_are_excluded(self):
        make_article(slug="draft-article", headline="Draft Headline", status=Article.Status.DRAFT)
        response = self.client.get(reverse("article_archive"))
        self.assertNotContains(response, "Draft Headline")

    def test_pagination_splits_across_pages(self):
        # Page size is 12 — 13 articles means page 2 has exactly 1.
        for i in range(13):
            make_article(slug=f"article-{i}", headline=f"Headline {i}")

        page_1 = self.client.get(reverse("article_archive"))
        self.assertEqual(len(page_1.context["page_obj"]), 12)

        page_2 = self.client.get(reverse("article_archive") + "?page=2")
        self.assertEqual(len(page_2.context["page_obj"]), 1)


# ── SEO: favicon, meta tags, robots.txt, sitemap.xml ────────────────────────

class SEOTest(TestCase):
    """
    Site-wide SEO/sharing basics: favicon links, meta description +
    Open Graph/Twitter tags, robots.txt, sitemap.xml. Lives here
    alongside BaseTemplateTest/ErrorPagesTest as the home for
    site-wide/base.html-level checks not owned by one specific app.
    """

    def test_favicon_links_present(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, "favicon.svg")
        self.assertContains(response, "favicon.ico")
        self.assertContains(response, "apple-touch-icon.png")

    def test_default_meta_description_present(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, '<meta name="description" content="Notable sales, agent moves')

    def test_og_and_twitter_tags_present(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, 'property="og:title"')
        self.assertContains(response, 'property="og:description"')
        self.assertContains(response, 'property="og:image"')
        self.assertContains(response, 'property="og:url"')
        self.assertContains(response, 'name="twitter:card" content="summary_large_image"')

    def test_article_detail_overrides_meta_description(self):
        make_article(
            slug="meta-article", headline="Meta Headline",
            subheadline="A specific subheadline for sharing.",
        )
        response = self.client.get(reverse("article_detail", args=["meta-article"]))
        self.assertContains(response, "A specific subheadline for sharing.")

    def test_article_detail_og_type_is_article(self):
        make_article(slug="og-type-article", headline="OG Type Article")
        response = self.client.get(reverse("article_detail", args=["og-type-article"]))
        self.assertContains(response, 'property="og:type" content="article"')

    def test_article_detail_og_image_uses_hero_image(self):
        make_article(
            slug="hero-image-article", headline="Hero Image Article",
            hero_image_url="https://images.example.com/hero.jpg",
        )
        response = self.client.get(reverse("article_detail", args=["hero-image-article"]))
        self.assertContains(response, "https://images.example.com/hero.jpg")

    def test_robots_txt_returns_200(self):
        response = self.client.get("/robots.txt")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/plain")

    def test_robots_txt_references_sitemap(self):
        response = self.client.get("/robots.txt")
        self.assertContains(response, "Sitemap:")
        self.assertContains(response, "/sitemap.xml")

    def test_sitemap_returns_200(self):
        response = self.client.get("/sitemap.xml")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/xml")

    def test_sitemap_includes_published_article(self):
        make_article(slug="sitemap-article", headline="Sitemap Article")
        response = self.client.get("/sitemap.xml")
        self.assertContains(response, "/articles/sitemap-article/")

    def test_sitemap_excludes_draft_article(self):
        make_article(slug="sitemap-draft", headline="Sitemap Draft", status=Article.Status.DRAFT)
        response = self.client.get("/sitemap.xml")
        self.assertNotContains(response, "/articles/sitemap-draft/")

    def test_sitemap_includes_static_pages(self):
        response = self.client.get("/sitemap.xml")
        self.assertContains(response, reverse("home"))
        self.assertContains(response, reverse("about"))
