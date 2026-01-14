from django.urls import path
from . import views

from django.contrib.sitemaps.views import sitemap
from .sitemaps import CountryRuleSitemap

sitemaps = {
    'countries': CountryRuleSitemap,
}

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('privacy/', views.privacy, name='privacy'),
    path('terms/', views.terms, name='terms'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('image-converter/', views.image_converter, name='image_converter'),
    path('<slug:slug>/', views.tool_view, name='tool_detail'),
    path('api/upload/<slug:slug>/', views.upload_photo, name='api_upload'),
    path('api/status/<int:photo_id>/', views.check_status, name='api_status'),
]
