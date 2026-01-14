import json
import os
import re
from django.core.management.base import BaseCommand
from passport_tool.models import CountryRule, SiteSettings
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Final precise cleanup and categorization for SnapFixer'

    def handle(self, *args, **options):
        # 1. Flag mapping
        flags = {
            "India": "🇮🇳", "USA": "🇺🇸", "UK": "🇬🇧", "Canada": "🇨🇦", "Australia": "🇦🇺",
            "Schengen Area": "🇪🇺", "UAE": "🇦🇪", "Saudi Arabia": "🇸🇦", "Singapore": "🇸🇬",
            "Pakistan": "🇵🇰", "Bangladesh": "🇧🇩", "Sri Lanka": "🇱🇰", "Nepal": "🇳🇵",
            "Philippines": "🇵🇭", "Malaysia": "🇲🇾", "Indonesia": "🇮🇩", "Thailand": "🇹🇭",
            "China": "🇨🇳", "Japan": "🇯🇵", "South Korea": "🇰🇷", "Brazil": "🇧🇷",
            "Mexico": "🇲🇽", "Russia": "🇷🇺", "Turkey": "🇹🇷"
        }

        # 2. Add utility tools
        utility_tools = [
            ("Signature Resizer", "signature-resizer", 35, 45, True, False),
            ("Compress Image to 20KB", "compress-image-20kb", 35, 45, True, False),
            ("Printable Sheets", "printable-sheets", 35, 45, True, False),
        ]
        for name, slug, w, h, is_tool, is_exam in utility_tools:
            CountryRule.objects.update_or_create(
                slug=slug,
                defaults={
                    'country': name,
                    'exam_country': 'Global',
                    'width_mm': w,
                    'height_mm': h,
                    'is_tool': is_tool,
                    'is_exam': is_exam,
                    'meta_title': f"{name} - Free Online Tool",
                    'meta_description': f"Free online {name}. Quick and easy.",
                    'content_body': f"Use our free {name} tool.",
                }
            )

        # 3. Load lookup map from JSON
        json_path = os.path.join(os.getcwd(), 'global_photo_rules.json')
        doc_to_country = {}
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                data = json.load(f)
                for entry in data:
                    cname = entry['country_name']
                    for doc in entry['documents']:
                        doc_to_country[doc['name']] = cname

        # 4. Correct all entries
        seen_slugs = set()
        
        # Priority order: Fix entries by category
        for rule in CountryRule.objects.all():
            if rule.is_tool: 
                seen_slugs.add(rule.slug)
                continue

            orig_name = rule.country # e.g. "Indian Passport"
            
            # Find the country it belongs to
            c_name = doc_to_country.get(orig_name, "Other")
            if c_name == "Other":
                for country in flags.keys():
                    if country.lower() in orig_name.lower():
                        c_name = country
                        break
            
            # Clean document name: "Indian Passport" -> "Passport"
            clean_doc_name = orig_name
            if c_name != "Other" and c_name.lower() in orig_name.lower():
                clean_doc_name = re.sub(re.escape(c_name), '', orig_name, flags=re.IGNORECASE).strip()
                # Also remove adjectives: "Indian" -> ""
                if c_name == "India": clean_doc_name = re.sub(r'Indian', '', clean_doc_name, flags=re.IGNORECASE).strip()
                elif c_name == "USA": clean_doc_name = re.sub(r'US', '', clean_doc_name, flags=re.IGNORECASE).strip()
                elif c_name == "UK": clean_doc_name = re.sub(r'UK', '', clean_doc_name, flags=re.IGNORECASE).strip()

            if not clean_doc_name:
                clean_doc_name = "Passport"

            # Re-detect type
            is_visa = "Visa" in orig_name or "BRP" in orig_name or "Green Card" in orig_name
            is_exam = "Exam" in orig_name or any(x in orig_name for x in ["SSC", "UPSC", "NEET", "JEE", "GATE", "PSC", "IBPS", "RRB"])
            
            # Handle India Exam hierarchies specifically
            exam_state = None
            exam_org = None
            if is_exam and c_name == "India":
                if "TNPSC" in orig_name or "Tamil Nadu" in orig_name:
                    exam_state = "Tamil Nadu"
                    exam_org = "TNPSC"
                elif "KPSC" in orig_name or "Kerala" in orig_name:
                    exam_state = "Kerala"
                    exam_org = "KPSC"
                elif "SSC" in orig_name:
                    exam_state = "Central"
                    exam_org = "SSC"
                elif "UPSC" in orig_name:
                    exam_state = "Central"
                    exam_org = "UPSC"
                # Add more as needed...
            
            if is_visa:
                exam_org = "Visa"
            
            # Update the rule
            rule.country = clean_doc_name
            rule.exam_country = c_name
            rule.flag_emoji = flags.get(c_name, "🏳️")
            rule.is_exam = is_exam or is_visa
            rule.exam_state = exam_state
            rule.exam_organization = exam_org
            
            # Slugs
            if is_visa:
                rule.slug = slugify(f"{c_name} {clean_doc_name}")
            elif is_exam:
                rule.slug = slugify(f"{exam_org or ''} {clean_doc_name} {c_name}")
            else:
                rule.slug = slugify(f"{c_name} {clean_doc_name}")

            # Safety check: if Custom Size, keep its special slug
            if "Custom Size" in orig_name:
                rule.slug = "custom-size-passport-photo"
                rule.country = "Custom Size"
                rule.exam_country = "Global"

            if rule.slug in seen_slugs:
                self.stdout.write(f"Deleting duplicate: {rule.slug}")
                rule.delete()
                continue
            
            seen_slugs.add(rule.slug)
            
            # Clean meta fields if they became ugly
            rule.h1 = f"{c_name} {clean_doc_name} Photo Maker"
            rule.meta_title = f"{c_name} {clean_doc_name} Photo Size & Maker"
            
            rule.save()

        self.stdout.write(self.style.SUCCESS("Success: Cleaned and Categorized!"))
