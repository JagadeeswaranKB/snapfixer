from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import CountryRule
from datetime import datetime

class CountryRuleSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9
    protocol = 'https'

    def items(self):
        return CountryRule.objects.all().order_by('country')

    def location(self, item):
        return reverse('tool_detail', kwargs={'slug': item.slug})
    
    def lastmod(self, item):
        # Return current date as these are dynamic tools
        return datetime.now()

class StaticViewSitemap(Sitemap):
    priority = 1.0  # Home page gets highest priority
    changefreq = 'daily'
    protocol = 'https'

    def items(self):
        return [
            {'name': 'home', 'priority': 1.0, 'changefreq': 'daily'},
            {'name': 'image_converter', 'priority': 0.8, 'changefreq': 'weekly'},
        ]

    def location(self, item):
        return reverse(item['name'])
    
    def priority(self, item):
        return item.get('priority', 0.6)
    
    def changefreq(self, item):
        return item.get('changefreq', 'weekly')
    
    def lastmod(self, item):
        return datetime.now()
