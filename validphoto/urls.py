from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

from django.contrib.sitemaps.views import sitemap
from passport_tool.sitemaps import CountryRuleSitemap, StaticViewSitemap
from blog.sitemaps import BlogPostSitemap

sitemaps = {
    'countries': CountryRuleSitemap,
    'static': StaticViewSitemap,
    'blog': BlogPostSitemap,
}

urlpatterns = [
    path('secure-portal/', admin.site.urls),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path('i18n/', include('django.conf.urls.i18n')),
    path('blog/', include('blog.urls')),
    path('', include('passport_tool.urls')),
    path("ckeditor5/", include('django_ckeditor_5.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
