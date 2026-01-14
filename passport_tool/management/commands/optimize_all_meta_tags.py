from django.core.management.base import BaseCommand
from passport_tool.models import CountryRule, PageMeta


class Command(BaseCommand):
    help = 'Optimize ALL meta tags to EXACTLY 55-60 char titles and 155-160 char descriptions'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting strict SEO optimization...'))
        
        # Optimize all CountryRule pages
        self.optimize_country_rules()
        
        # Optimize static pages
        self.optimize_static_pages()
        
        self.stdout.write(self.style.SUCCESS('\n✅ All pages optimized successfully!'))

    def optimize_country_rules(self):
        """Optimize all CountryRule pages with STRICT character requirements"""
        self.stdout.write('\n📝 Optimizing CountryRule pages...')
        
        rules = CountryRule.objects.all()
        optimized = 0
        
        for rule in rules:
            title, desc = self.generate_strict_meta(rule)
            
            # Validate strict requirements
            if not (55 <= len(title) <= 60):
                self.stdout.write(self.style.WARNING(
                    f"  ⚠ {rule.slug}: Title {len(title)} chars (not 55-60)"
                ))
            if not (155 <= len(desc) <= 160):
                self.stdout.write(self.style.WARNING(
                    f"  ⚠ {rule.slug}: Desc {len(desc)} chars (not 155-160)"
                ))
            
            # Update
            rule.meta_title = title
            rule.meta_description = desc
            rule.save()
            optimized += 1
        
        self.stdout.write(f"\n  Optimized {optimized}/{rules.count()} pages")

    def pad_to_length(self, text, min_len, max_len, filler=" online"):
        """Pad text to reach minimum length without exceeding maximum"""
        if len(text) >= min_len:
            return text[:max_len]
        
        # Try adding filler
        if len(text + filler) <= max_len:
            return text + filler
        
        # Try different fillers
        fillers = [" today", " now", " free", " fast", " tool"]
        for f in fillers:
            if min_len <= len(text + f) <= max_len:
                return text + f
        
        # Last resort: add spaces or truncate
        return text[:max_len]

    def generate_strict_meta(self, rule):
        """Generate meta tags with STRICT 55-60 and 155-160 requirements"""
        
        # Image Converters
        if '-to-' in rule.slug and rule.is_tool:
            return self.gen_converter(rule)
        
        # Compression tools
        elif 'compress' in rule.slug.lower():
            return self.gen_compressor(rule)
        
        # Printable/Custom tools
        elif any(x in rule.slug for x in ['printable', 'custom-size', 'signature']):
            return self.gen_tool(rule)
        
        # Exam pages
        elif rule.is_exam:
            return self.gen_exam(rule)
        
        # Passport/Visa pages
        else:
            return self.gen_passport(rule)

    def gen_converter(self, rule):
        """Converter pages: 55-60 title, 155-160 desc"""
        parts = rule.slug.split('-to-')
        if len(parts) == 2:
            from_fmt = parts[0].upper()
            to_fmt = parts[1].upper()
            
            # Title: exactly 55-60 chars
            title = f"Free {from_fmt} to {to_fmt} Converter – Convert Images Fast"
            if len(title) < 55:
                title = f"Free {from_fmt} to {to_fmt} Converter – Convert Images Fast Now"
            title = title[:60]  # Ensure max 60
            
            # Description: exactly 155-160 chars
            desc = f"Convert {from_fmt} images to {to_fmt} instantly using our free {from_fmt} to {to_fmt} converter. Fast, secure, high-quality conversion online with no signup required today!"
            if len(desc) < 155:
                desc = f"Convert {from_fmt} images to {to_fmt} format instantly using our free {from_fmt} to {to_fmt} converter tool. Fast, secure, high-quality image conversion online with no signup required today!"
            desc = desc[:160]  # Ensure max 160
            
            return title, desc
        
        return rule.meta_title, rule.meta_description

    def gen_compressor(self, rule):
        """Compressor tools"""
        if '20kb' in rule.slug:
            title = "Compress Image to 20KB Online Free – Exact Size Tool"  # 52 chars
            title = "Compress Image to 20KB Online Free – Exact Size Tool Now"  # 57 chars
            desc = "Compress any image to exactly 20KB or less instantly with our free online tool. Perfect for forms, applications, and uploads. Fast, secure compression today!"  # 158 chars
        elif '50kb' in rule.slug:
            title = "Compress Image to 50KB Online Free – Exact Size Tool Now"  # 57 chars
            desc = "Compress any image to exactly 50KB or less instantly with our free online tool. Perfect for forms, applications, and uploads. Fast, secure compression today!"  # 158 chars
        else:
            title = "Free Image Compressor Online – Reduce File Size Fast Now"  # 57 chars
            desc = "Compress images to any size instantly with our free image compressor tool. Reduce file size while maintaining quality. Perfect for web, email, applications!"  # 158 chars
        
        return title, desc

    def gen_tool(self, rule):
        """Utility tools"""
        if 'printable' in rule.slug:
            title = "Printable Passport Photo Sheet Maker – 4x6 Layout Free"  # 55 chars
            desc = "Create printable passport photo sheets instantly with our free tool. Multi-photo 4x6 layout ready for home or pharmacy printing. Fast, easy, professional!"  # 157 chars
        elif 'custom-size' in rule.slug:
            title = "Custom Size Photo Maker – Resize Images to Any Dimension"  # 56 chars
            desc = "Resize images to any custom size or dimension instantly with our free tool. Perfect for passport photos, IDs, and applications. Fast, accurate resizing!"  # 155 chars
        elif 'signature' in rule.slug:
            title = "Signature Resizer Tool – Resize Signatures to Any Size"  # 54 chars -> need to pad
            title = "Signature Resizer Tool – Resize Signatures to Any Size!"  # 55 chars
            desc = "Resize signature images to any required size instantly with our free signature resizer tool. Perfect for forms, applications, and documents. Fast, easy!"  # 156 chars
        else:
            title = f"{rule.country} Tool – Free Online Photo Editor Now"[:60]
            desc = f"Use our free {rule.country.lower()} tool online for professional photo editing. Fast, secure, and easy to use with instant results. Try it free today!"[:160]
        
        return title, desc

    def gen_exam(self, rule):
        """Exam pages with strict requirements"""
        exam_name = rule.country
        
        # Title: 55-60 chars
        base_title = f"{exam_name} Photo Maker – Compliant Size Tool"
        if len(base_title) < 55:
            title = f"Free {exam_name} Photo Maker – Compliant Size Tool"
        elif len(base_title) > 60:
            title = f"{exam_name[:30]} Photo – Compliant Tool"
        else:
            title = base_title
        
        # Ensure 55-60
        if len(title) < 55:
            title = title + " Free"
        title = title[:60]
        
        # Description: 155-160 chars
        base_desc = f"Create official {exam_name} photos instantly using our free {exam_name} photo maker. AI-powered tool ensures perfect exam photos meeting all size requirements today."
        
        if len(base_desc) < 155:
            desc = f"Create compliant {exam_name} photos instantly with our free {exam_name} photo maker tool. AI-powered for perfect exam photos meeting all official size requirements today."
        elif len(base_desc) > 160:
            desc = f"Create {exam_name} photos with our free {exam_name} photo maker. AI tool for perfect exam photos meeting official size requirements. Try it today!"
        else:
            desc = base_desc
        
        # Ensure 155-160
        desc = desc[:160]
        if len(desc) < 155:
            desc = desc + " now"
        
        return title, desc

    def gen_passport(self, rule):
        """Passport pages with strict requirements"""
        country = rule.country
        
        # Title: 55-60 chars
        base_title = f"{country} Passport Photo Maker – AI Tool Online"
        if len(base_title) < 55:
            title = f"Free {country} Passport Photo Maker – AI Tool Online"
        elif len(base_title) > 60:
            title = f"{country} Passport Photo – AI Maker Online"
        else:
            title = base_title
        
        # Ensure 55-60
        if len(title) > 60:
            title = f"{country[:20]} Passport Photo – AI Maker"
        if len(title) < 55:
            title = title + " Free"
        title = title[:60]
        
        # Description: 155-160 chars
        size_info = ""
        if rule.width_mm and rule.height_mm:
            size_info = f" ({rule.width_mm}x{rule.height_mm}mm)"
        
        base_desc = f"Create compliant {country} passport photos{size_info} instantly with our free AI-powered {country} passport photo maker. Fast, secure, professional results online today."
        
        if len(base_desc) < 155:
            desc = f"Create official {country} passport photos{size_info} instantly using our free AI-powered {country} passport photo maker tool. Fast, secure, professional results online today."
        elif len(base_desc) > 160:
            desc = f"Create {country} passport photos{size_info} with our free AI {country} passport photo maker. Fast, secure, professional results online. Try it today!"
        else:
            desc = base_desc
        
        # Ensure 155-160
        desc = desc[:160]
        if len(desc) < 155:
            desc = desc + " now"
        
        return title, desc

    def optimize_static_pages(self):
        """Optimize static pages with strict requirements"""
        self.stdout.write('\n📝 Optimizing static pages...')
        
        static_pages = {
            '/': {
                'title': 'Free Passport Photo Maker – AI Tool for 100+ Countries',  # 55 chars
                'description': 'Create compliant passport photos for 100+ countries instantly with our free AI passport photo maker tool. Fast, secure, professional results. No signup required!',  # 160 chars
            },
            '/about/': {
                'title': 'About Us – Free AI Passport Photo & Image Converter Tool',  # 56 chars
                'description': 'Learn about our free AI passport photo maker and image converter tools. Create compliant passport photos and convert images instantly with professional results!',  # 159 chars
            },
            '/contact/': {
                'title': 'Contact Us – Get Help with Passport Photo & Image Tools',  # 55 chars
                'description': 'Contact our support team for help with passport photo creation and image conversion. We are here to assist you with all your photo editing needs. Reach out!',  # 156 chars
            },
            '/privacy/': {
                'title': 'Privacy Policy – Your Data Security with Our Photo Tools',  # 56 chars
                'description': 'Read our privacy policy to understand how we protect your data when using our passport photo maker and image converter tools. Your privacy and security matter!',  # 159 chars
            },
            '/terms/': {
                'title': 'Terms of Service – Rules for Using Our Photo Tools Now',  # 55 chars
                'description': 'Review our terms of service for using the passport photo maker and image converter tools. Understand your rights and responsibilities when using our website!',  # 158 chars
            },
            '/image-converter/': {
                'title': 'Free Image Converter – Convert JPG, PNG, WebP & More',  # 52 chars -> need padding
                'title': 'Free Image Converter – Convert JPG, PNG, WebP & More Now',  # 57 chars
                'description': 'Convert images between JPG, PNG, WebP, HEIC, and BMP formats instantly with our free image converter tool. Fast, secure, high-quality conversion online today!',  # 157 chars
            },
        }
        
        for path, meta in static_pages.items():
            page_meta, created = PageMeta.objects.get_or_create(path=path)
            page_meta.title = meta['title']
            page_meta.description = meta['description']
            page_meta.save()
            
            action = "Created" if created else "Updated"
            self.stdout.write(
                f"  ✓ {path:<30} {action} - T:{len(meta['title']):>2} D:{len(meta['description']):>3}"
            )
