from django.core.management.base import BaseCommand
from passport_tool.models import CountryRule, SiteSettings
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Cleanup duplicate rules, add flags, and categorize correctly'

    def handle(self, *args, **options):
        # 1. Flag mapping (Simplified version)
        flags = {
            "India": "🇮🇳", "USA": "🇺🇸", "UK": "🇬🇧", "Canada": "🇨🇦", "Australia": "🇦🇺",
            "Schengen Area": "🇪🇺", "UAE": "🇦🇪", "Saudi Arabia": "🇸🇦", "Singapore": "🇸🇬",
            "Pakistan": "🇵🇰", "Bangladesh": "🇧🇩", "Sri Lanka": "🇱🇰", "Nepal": "🇳🇵",
            "Philippines": "🇵🇭", "Malaysia": "🇲🇾", "Indonesia": "🇮🇩", "Thailand": "🇹🇭",
            "China": "🇨🇳", "Japan": "🇯🇵", "South Korea": "🇰🇷", "Brazil": "🇧🇷",
            "Mexico": "🇲🇽", "Russia": "🇷🇺", "Turkey": "🇹🇷"
        }

        # 2. Add utility tools if missing
        utility_tools = [
            ("Signature Resizer", "signature-resizer", 35, 45, True),
            ("Compress Image to 20KB", "compress-image-20kb", 35, 45, True),
            ("Printable Sheets", "printable-sheets", 35, 45, True),
        ]
        for name, slug, w, h, is_tool in utility_tools:
            CountryRule.objects.update_or_create(
                slug=slug,
                defaults={
                    'country': name,
                    'width_mm': w,
                    'height_mm': h,
                    'is_tool': is_tool,
                    'meta_title': f"{name} - Free Online Tool",
                    'meta_description': f"Free online {name}. Quick and easy.",
                    'content_body': f"Use our free {name} tool.",
                }
            )

        # 3. Process all rules
        all_rules = CountryRule.objects.all()
        seen_slugs = set()
        
        for rule in all_rules:
            # Add flag
            for country, flag in flags.items():
                if country.lower() in rule.country.lower() or (rule.exam_country and country.lower() in rule.exam_country.lower()):
                    rule.flag_emoji = flag
                    break
            
            # Recategorize Visas
            if "Visa" in rule.country or "BRP" in rule.country:
                if not rule.exam_country:
                    # Logic to find which country this visa belongs to
                    for c in flags.keys():
                        if c in rule.slug:
                            rule.exam_country = c
                            break
                rule.is_exam = True
                rule.exam_organization = "Visa"
            
            # Deduplicate by slug
            if rule.slug in seen_slugs:
                rule.delete()
                continue
            
            seen_slugs.add(rule.slug)
            rule.save()

        # 4. Initialize SiteSettings if logo/favicon are missing to avoid 500
        settings = SiteSettings.load()
        self.stdout.write(self.style.SUCCESS("Cleanup completed!"))
