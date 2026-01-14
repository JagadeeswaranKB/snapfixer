import json
import os
import re
from django.core.management.base import BaseCommand
from passport_tool.models import CountryRule, SiteSettings, PageMeta
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Aggressive cleanup: Recovery of 100% SEO and exhaustive Indian State Hierarchy'

    def handle(self, *args, **options):
        self.stdout.write("Starting Exhaustive Database Optimization...")
        
        # 1. Comprehensive Regional List
        indian_regions = {
            "Andhra Pradesh": ["AP ", "Andhra"], "Arunachal Pradesh": ["Arunachal"], "Assam": ["Assam"],
            "Bihar": ["Bihar"], "Chhattisgarh": ["Chhattisgarh"], "Goa": ["Goa"], "Gujarat": ["Gujarat"],
            "Haryana": ["Haryana"], "Himachal Pradesh": ["Himachal"], "Jharkhand": ["Jharkhand"],
            "Karnataka": ["Karnataka"], "Kerala": ["Kerala", "KPSC"], "Madhya Pradesh": ["MP ", "Madhya"],
            "Maharashtra": ["Maharashtra", "Maha"], "Manipur": ["Manipur"], "Meghalaya": ["Meghalaya"],
            "Mizoram": ["Mizoram"], "Nagaland": ["Nagaland"], "Odisha": ["Odisha", "Orissa"],
            "Punjab": ["Punjab"], "Rajasthan": ["Rajasthan"], "Sikkim": ["Sikkim"],
            "Tamil Nadu": ["Tamil Nadu", "Tamilnadu", "TN ", "TNPSC"], "Telangana": ["Telangana"],
            "Tripura": ["Tripura"], "Uttar Pradesh": ["UP ", "Uttar"], "Uttarakhand": ["Uttarakhand"],
            "West Bengal": ["West Bengal", "Bengal"], "Delhi": ["Delhi"], "Puducherry": ["Puducherry"],
            "Chandigarh": ["Chandigarh"], "Jammu and Kashmir": ["Jammu", "Kashmir", "J&K"],
            "Ladakh": ["Ladakh"], "Andaman and Nicobar": ["Andaman"], "Lakshadweep": ["Lakshadweep"]
        }

        flags = {
            "India": "🇮🇳", "USA": "🇺🇸", "UK": "🇬🇧", "Canada": "🇨🇦", "Australia": "🇦🇺",
            "Schengen Area": "🇪🇺", "UAE": "🇦🇪", "Saudi Arabia": "🇸🇦", "Singapore": "🇸🇬",
            "Pakistan": "🇵🇰", "Bangladesh": "🇧🇩", "Sri Lanka": "🇱🇰", "Nepal": "🇳🇵",
            "Philippines": "🇵🇭", "Malaysia": "🇲🇾", "Indonesia": "🇮🇩", "Thailand": "🇹🇭"
        }

        # 2. Process all rules
        seen_slugs = set()
        for rule in CountryRule.objects.all().order_by('id'):
            if rule.is_tool:
                seen_slugs.add(rule.slug)
                continue

            orig_name = (rule.country or "Unknown").strip()
            
            # a. Improved Country/State/Org Detection
            c_name = "Other"
            detected_state = None
            detected_org = None
            
            # Check for Indian States/UTs
            for state, aliases in indian_regions.items():
                if any(re.search(re.escape(a), orig_name, re.I) for a in aliases + [state]):
                    detected_state = state
                    c_name = "India"
                    break
            
            # Base Country Detection
            if c_name == "Other":
                for country in flags.keys():
                    if re.search(re.escape(country), orig_name, re.I):
                        c_name = country
                        break
            
            # Clean Name
            clean_name = orig_name
            # Remove country name
            if c_name != "Other":
                clean_name = re.sub(re.escape(c_name), '', clean_name, flags=re.I).strip()
            # Remove state name if detected
            if detected_state:
                clean_name = re.sub(re.escape(detected_state), '', clean_name, flags=re.I).strip()
            # Specific redundant removals
            clean_name = re.sub(r'^(Photo|Passport|Visa|Exam|Indian|US|US\s+|UK\s+|British)\s+', '', clean_name, flags=re.I).strip()
            
            if not clean_name or clean_name.lower() in ["maker", "tool"]:
                clean_name = "Passport"

            # Detect Org
            if "TNPSC" in orig_name: detected_org = "TNPSC"
            elif "KPSC" in orig_name or "Kerala PSC" in orig_name: detected_org = "KPSC"
            elif "SSC" in orig_name: detected_org = "SSC"
            elif "UPSC" in orig_name: detected_org = "UPSC"
            elif "JEE" in orig_name: detected_org = "JEE"
            elif "NEET" in orig_name: detected_org = "NEET"
            
            is_visa = "Visa" in orig_name or "BRP" in orig_name or "Green Card" in orig_name
            is_exam = detected_org or detected_state or "Exam" in orig_name or any(x in orig_name.upper() for x in ["PSC", "CET", "GATE"])
            
            if is_visa: detected_org = "Visa"

            # b. Update Rule
            rule.country = clean_name
            rule.exam_country = c_name
            rule.flag_emoji = flags.get(c_name, "🏳️")
            rule.is_exam = is_exam or is_visa
            rule.exam_state = detected_state
            rule.exam_organization = detected_org or ("Other" if is_exam else None)

            # c. Perfect Slugs
            if is_visa:
                rule.slug = slugify(f"{c_name} {clean_name} photo maker")
            elif is_exam:
                rule.slug = slugify(f"{detected_org or ''} {clean_name} {detected_state or c_name} photo maker")
            else:
                rule.slug = slugify(f"{c_name} {clean_name} photo maker")

            if rule.slug in seen_slugs:
                rule.delete()
                continue
            seen_slugs.add(rule.slug)

            # d. STRICT SEO (55-60 titles, 155-160 descs)
            # Use dynamic keyword based on type
            kw = clean_name if not is_visa else f"{c_name} {clean_name}"
            
            # Title: exactly 55-60
            title = f"Free {kw} Photo Maker – AI Powered Compliant Tool Online"
            if len(title) > 60: title = f"{kw} Photo Maker – AI Compliant Tool Online"
            if len(title) < 55: title = f"Free {kw} Photo Maker – AI Powered Compliant Tool Online Today!"
            rule.meta_title = title[:60].strip()
            
            # Desc: exactly 155-160
            desc_base = f"Create official {kw} photos instantly using our free AI-powered photo maker tool. 100% compliant with the latest government standards and size requirements for 2026."
            if len(desc_base) < 155:
                desc_base += " Fast, secure, and easy to use with instant high-quality results for everyone now today!"
            rule.meta_description = desc_base[:160].strip()

            rule.save()

        self.stdout.write(self.style.SUCCESS("Exhaustive Cleanup & 100% SEO Optimization Finished!"))
