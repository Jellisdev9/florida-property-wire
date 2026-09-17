"""
Root URL configuration for the Florida Property Wire backend.

URL routing works like a switch statement — Django checks each path() in
order and calls the view function for the first match.

We keep all existing /api/ routes intact (the DRF API is still useful for
mobile/RSS/future use) and add the new template-rendered page URLs below them.
"""
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include, reverse
from django.http import HttpResponse, JsonResponse

# Import the template views — these render HTML pages
from articles.views import home_view, article_detail_view, article_archive_view, about_view
from sales.views import notable_sales_view, sale_detail_view
from market.views import market_pulse_view, agents_view, neighborhoods_view
from subscribers.views import subscribe_view, unsubscribe_view
from .sitemaps import sitemaps


def health_check(request):
    return JsonResponse({"status": "ok"})


def robots_txt(request):
    # Built from the request rather than a hardcoded domain, so it's
    # correct on localhost, staging-like environments, and production
    # alike without needing a SITE_ADDRESS-style setting of its own.
    sitemap_url = request.build_absolute_uri(reverse("sitemap"))
    content = f"User-agent: *\nAllow: /\n\nSitemap: {sitemap_url}\n"
    return HttpResponse(content, content_type="text/plain")


urlpatterns = [
    # ── Django admin ──────────────────────────────────────────────────────────
    path("admin/", admin.site.urls),

    # ── Health check ──────────────────────────────────────────────────────────
    path("api/healthz/", health_check),

    # ── SEO ───────────────────────────────────────────────────────────────────
    path("robots.txt", robots_txt),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),

    # ── DRF API routes (kept — costs nothing, useful for mobile/RSS later) ───
    # include() pulls in the urlpatterns list from each app's urls.py
    path("api/", include("articles.urls")),
    path("api/", include("sales.urls")),
    path("api/", include("market.urls")),
    path("api/", include("subscribers.urls")),

    # ── Template-rendered pages ───────────────────────────────────────────────
    # The name= argument lets views/templates use reverse('home') or
    # {% url 'home' %} instead of hardcoding the URL string.

    # Homepage — "" matches the root path "/"
    path("", home_view, name="home"),

    # Article archive — all published articles, paginated, newest first
    path("articles/", article_archive_view, name="article_archive"),

    # Individual article page — <slug:slug> captures URL-safe strings like
    # "naples-bayfront-estate" and passes them as the 'slug' keyword argument
    path("articles/<slug:slug>/", article_detail_view, name="article_detail"),

    # Notable sales grid
    path("notable-sales/", notable_sales_view, name="notable_sales"),

    # Individual sale detail page
    path("notable-sales/<slug:slug>/", sale_detail_view, name="sale_detail"),

    # Market Pulse — Market Pulse category articles
    path("market-pulse/", market_pulse_view, name="market_pulse"),

    # Agents — full Top Agents leaderboard + Agent Watch articles
    path("agents/", agents_view, name="agents"),

    # Neighborhoods — full Neighborhood Watch grid + articles
    path("neighborhoods/", neighborhoods_view, name="neighborhoods"),

    # About — static masthead page
    path("about/", about_view, name="about"),

    # Newsletter subscribe — POST only (the view enforces this with @require_POST)
    path("subscribe/", subscribe_view, name="subscribe"),

    # Newsletter unsubscribe — self-service page, GET shows the form, POST processes it
    path("unsubscribe/", unsubscribe_view, name="unsubscribe"),
]
