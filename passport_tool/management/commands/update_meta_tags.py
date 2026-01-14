from django.core.management.base import BaseCommand
from passport_tool.models import CountryRule, PageMeta


class Command(BaseCommand):
    help = 'Update meta tags for all pages to be SEO-optimized with proper character limits'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting SEO meta tags optimization...'))
        
        # Update image converter pages
        self.update_converters()
        
        # Update static pages
        self.update_static_pages()
        
        self.stdout.write(self.style.SUCCESS('\n✅ All meta tags updated successfully!'))

    def update_converters(self):
        """Update meta tags for all image converter pages"""
        self.stdout.write('\n📝 Updating image converter pages...')
        
        converters = {
            'webp-to-jpg': {
                'title': 'Free WebP to JPG Converter – Convert Images Easily',
                'description': 'Convert WebP images to JPG instantly using our free WebP to JPG converter. Fast, secure, high-quality conversion online with no signup required today!',
            },
            'webp-to-png': {
                'title': 'Free WebP to PNG Converter – Convert Images Easily',
                'description': 'Convert WebP images to PNG instantly using our free WebP to PNG converter. Fast, secure, high-quality conversion online with no signup required today!',
            },
            'heic-to-jpg': {
                'title': 'Free HEIC to JPG Converter – Convert Images Easily',
                'description': 'Convert HEIC images to JPG instantly using our free HEIC to JPG converter. Fast, secure, high-quality conversion online with no signup required today!',
            },
            'heic-to-png': {
                'title': 'Free HEIC to PNG Converter – Convert Images Easily',
                'description': 'Convert HEIC images to PNG instantly using our free HEIC to PNG converter. Fast, secure, high-quality conversion online with no signup required today!',
            },
            'heic-to-webp': {
                'title': 'Free HEIC to WebP Converter – Convert Images Easily',
                'description': 'Convert HEIC images to WebP using our free HEIC to WebP converter. Fast, secure, high-quality conversion online with no signup required. Try it today!',
            },
            'png-to-jpg': {
                'title': 'Free PNG to JPG Converter – Convert Images Easily',
                'description': 'Convert PNG images to JPG instantly using our free PNG to JPG converter. Fast, secure, high-quality conversion online with no signup required today now!',
            },
            'jpg-to-png': {
                'title': 'Free JPG to PNG Converter – Convert Images Easily',
                'description': 'Convert JPG images to PNG instantly using our free JPG to PNG converter. Fast, secure, high-quality conversion online with no signup required today now!',
            },
            'jpg-to-webp': {
                'title': 'Free JPG to WebP Converter – Convert Images Easily',
                'description': 'Convert JPG images to WebP using our free JPG to WebP converter. Fast, secure, high-quality conversion online with no signup required. Try it now today!',
            },
            'bmp-to-jpg': {
                'title': 'Free BMP to JPG Converter – Convert Images Easily',
                'description': 'Convert BMP images to JPG instantly using our free BMP to JPG converter. Fast, secure, high-quality conversion online with no signup required today now!',
            },
        }
        
        for slug, meta in converters.items():
            try:
                converter = CountryRule.objects.get(slug=slug)
                converter.meta_title = meta['title']
                converter.meta_description = meta['description']
                converter.save()
                
                title_len = len(meta['title'])
                desc_len = len(meta['description'])
                self.stdout.write(
                    f"  ✓ {slug}: Title={title_len} chars, Desc={desc_len} chars"
                )
            except CountryRule.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f"  ⚠ {slug} not found, skipping...")
                )

    def update_static_pages(self):
        """Update meta tags for static pages"""
        self.stdout.write('\n📝 Updating static pages...')
        
        static_pages = {
            '/about/': {
                'title': 'About Us – Free Online Passport Photo & Image Tools',
                'description': 'Learn about our free online passport photo maker and image converter tools. Create compliant passport photos and convert images instantly with AI power.',
            },
            '/contact/': {
                'title': 'Contact Us – Get Help with Passport Photo Tools',
                'description': 'Contact our support team for help with passport photo creation and image conversion. We\'re here to assist you with all your photo editing needs today.',
            },
            '/privacy/': {
                'title': 'Privacy Policy – Your Data Security with Our Photo Tools',
                'description': 'Read our privacy policy to understand how we protect your data when using our passport photo maker and image converter tools. Your privacy matters to us.',
            },
            '/terms/': {
                'title': 'Terms of Service – Rules for Using Our Photo Tools',
                'description': 'Review our terms of service for using the passport photo maker and image converter tools. Understand your rights and responsibilities when using our site.',
            },
            '/image-converter/': {
                'title': 'Free Image Converter – Convert JPG, PNG, WebP & More',
                'description': 'Convert images between JPG, PNG, WebP, HEIC, and BMP formats instantly. Free image converter tool with fast, secure, high-quality conversion online now!',
            },
        }
        
        for path, meta in static_pages.items():
            page_meta, created = PageMeta.objects.get_or_create(path=path)
            page_meta.title = meta['title']
            page_meta.description = meta['description']
            page_meta.save()
            
            title_len = len(meta['title'])
            desc_len = len(meta['description'])
            action = "Created" if created else "Updated"
            self.stdout.write(
                f"  ✓ {path}: {action} - Title={title_len} chars, Desc={desc_len} chars"
            )
