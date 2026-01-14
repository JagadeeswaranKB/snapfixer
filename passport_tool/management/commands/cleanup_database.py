import json
import os
import re
from django.core.management.base import BaseCommand
from passport_tool.models import CountryRule, SiteSettings, PageMeta
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Master Cleanup: Strict SEO, Full Hierarchy, and Stability Fix'

    def handle(self, *args, **options):
        self.stdout.write("Starting Master Database Cleanup...")
        
        # 1. Flag mapping
        flags = {
            "India": "🇮🇳", "USA": "🇺🇸", "UK": "🇬🇧", "Canada": "🇨🇦", "Australia": "🇦🇺",
            "Schengen Area": "🇪🇺", "UAE": "🇦🇪", "Saudi Arabia": "🇸🇦", "Singapore": "🇸🇬",
            "Pakistan": "🇵🇰", "Bangladesh": "🇧🇩", "Sri Lanka": "🇱🇰", "Nepal": "🇳🇵",
            "Philippines": "🇵🇭", "Malaysia": "🇲🇾", "Indonesia": "🇮🇩", "Thailand": "🇹🇭",
            "China": "🇨🇳", "Japan": "🇯🇵", "South Korea": "🇰🇷", "Brazil": "🇧🇷",
            "Mexico": "🇲🇽", "Russia": "🇷🇺", "Turkey": "🇹🇷"
        }

        # 2. Indian States List for automatic detection
        indian_states = [
            "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
            "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
            "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
            "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
            "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"
        ]

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

        seen_slugs = set()
        
        # 4. Process all CountryRule entries
        for rule in CountryRule.objects.all().order_by('id'):
            if rule.is_tool:
                seen_slugs.add(rule.slug)
                continue

            orig_name = rule.country or "Unknown"
            
            # a. Determine Country
            c_name = doc_to_country.get(orig_name, "Other")
            if c_name == "Other":
                for country in flags.keys():
                    if country.lower() in orig_name.lower():
                        c_name = country
                        break
            
            # b. Clean Document Name
            clean_doc_name = orig_name
            if c_name != "Other" and c_name.lower() in orig_name.lower():
                clean_doc_name = re.sub(re.escape(c_name), '', orig_name, flags=re.IGNORECASE).strip()
                # Remove common adjectives
                clean_doc_name = re.sub(r'^(Indian|US|UK|British|Canadian|Australian|Chinese)\s+', '', clean_doc_name, flags=re.IGNORECASE).strip()

            if not clean_doc_name:
                clean_doc_name = "Passport"

            # c. Detect Type and Hierarchy
            is_visa = "Visa" in orig_name or "BRP" in orig_name or "Green Card" in orig_name or "Residence Permit" in orig_name
            is_exam = "Exam" in orig_name or any(x in orig_name for x in ["SSC", "UPSC", "NEET", "JEE", "GATE", "PSC", "IBPS", "RRB", "KPSC", "TNPSC"])
            
            exam_state = None
            exam_org = None
            
            if is_exam and c_name == "India":
                # Detect state
                for state in indian_states:
                    if state.lower() in orig_name.lower():
                        exam_state = state
                        break
                
                # Common organizations
                if "TNPSC" in orig_name: exam_org = "TNPSC"
                elif "KPSC" in orig_name: exam_org = "KPSC"
                elif "SSC" in orig_name: exam_org = "SSC"
                elif "UPSC" in orig_name: exam_org = "UPSC"
                elif "Bank" in orig_name or "IBPS" in orig_name: exam_org = "IBPS"
                elif "Railway" in orig_name or "RRB" in orig_name: exam_org = "RRB"
                
                if not exam_state and not exam_org:
                    exam_state = "Central"
                    exam_org = "Standard"
                elif not exam_state:
                    exam_state = "Central"
            
            if is_visa:
                exam_org = "Visa"
            
            # d. Update Model Fields
            rule.country = clean_doc_name
            rule.exam_country = c_name
            rule.flag_emoji = flags.get(c_name, "🏳️")
            rule.is_exam = is_exam or is_visa
            rule.exam_state = exam_state
            rule.exam_organization = exam_org
            
            # e. SEO-Compliant Slugs
            # High quality slugs: "india-passport-photo-maker"
            if is_visa:
                target_slug = slugify(f"{c_name} {clean_doc_name} photo maker")
            elif is_exam:
                target_slug = slugify(f"{exam_org or ''} {clean_doc_name} {c_name} photo maker")
            else:
                target_slug = slugify(f"{c_name} {clean_doc_name} photo maker")

            # Handle Custom Size special case
            if "Custom Size" in orig_name:
                target_slug = "custom-size-passport-photo"
                rule.country = "Custom Size"
                rule.exam_country = "Global"

            if target_slug in seen_slugs:
                self.stdout.write(f"Merging duplicate: {target_slug}")
                rule.delete()
                continue
            
            rule.slug = target_slug
            seen_slugs.add(target_slug)

            # f. STRICT SEO Meta Tags (55-60 titles, 155-160 descs)
            title_name = f"{c_name} {clean_doc_name}"
            
            # Title Generation (Goal: 55-60)
            title = f"Free {title_name} Photo Maker – Compliant Tool Online"
            if len(title) < 55: title = f"Free {title_name} Photo Maker – AI Compliant Tool Online"
            if len(title) > 60: title = f"{title_name} Photo Maker – Official AI Tool Online"
            rule.meta_title = title[:60].strip()
            
            # Description Generation (Goal: 155-160)
            size_str = f"{rule.width_mm}x{rule.height_mm}mm"
            desc = f"Create official {title_name} photos ({size_str}) instantly with our free AI photo maker. 100% compliant with latest standards and requirements for 2026 today!"
            if len(desc) < 155: desc = f"Create official {title_name} photos ({size_str}) instantly with our free AI photo maker tool. 100% compliant with latest official standards and requirements for 2026!"
            rule.meta_description = desc[:160].strip()

            rule.save()

        # 5. Optimize Static Pages too
        static_pages = {
            '/': {
                'title': 'Free Passport Photo Maker – AI Tool for 100+ Countries',
                'description': 'Create compliant passport photos for 100+ countries instantly with our free AI passport photo maker tool. Fast, secure, professional results for everyone now!',
            },
            '/image-converter/': {
                'title': 'Free Image Converter – Convert JPG, PNG, WebP & All Now',
                'description': 'Convert images between JPG, PNG, WebP, HEIC, and BMP formats instantly with our free image converter tool. Fast, secure, high-quality conversion online today!',
            }
        }
        for path, meta in static_pages.items():
            pm, _ = PageMeta.objects.get_or_create(path=path)
            pm.title = meta['title']
            pm.description = meta['description']
            pm.save()

        self.stdout.write(self.style.SUCCESS("Master Cleanup and SEO Optimization finished!"))
