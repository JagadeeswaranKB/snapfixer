from django.db import migrations, models
from django.utils.text import slugify
import os

class CountryRule(models.Model):
    country = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True, max_length=255)
    flag_emoji = models.CharField(max_length=10, blank=True, default="🏳️", help_text="Country flag emoji")
    width_mm = models.IntegerField(help_text="Width in mm")
    height_mm = models.IntegerField(help_text="Height in mm")
    bg_color = models.CharField(max_length=20, default="white", help_text="e.g. white, lightblue")
    
    meta_title = models.CharField(max_length=200)
    meta_description = models.TextField()
    meta_keywords = models.CharField(max_length=255, blank=True, help_text="Comma-separated keywords")
    content_body = models.TextField(help_text="SEO content body")

    # Open Graph / Social Media
    og_title = models.CharField(max_length=200, blank=True, help_text="Open Graph title")
    og_description = models.TextField(blank=True, help_text="Open Graph description")
    og_image = models.ImageField(upload_to='tool/og/', blank=True, null=True, help_text="Social media share image")

    # Twitter Card
    twitter_title = models.CharField(max_length=200, blank=True, help_text="Twitter title")
    twitter_description = models.TextField(blank=True, help_text="Twitter description")
    twitter_image = models.ImageField(upload_to='tool/twitter/', blank=True, null=True, help_text="Twitter share image")

    canonical_url = models.CharField(max_length=255, blank=True, help_text="Full absolute URL if different from path")

    # Programmatic SEO Fields
    h1 = models.CharField(max_length=200, blank=True, help_text="Main heading for the page")
    intro_text = models.TextField(blank=True, help_text="Intro paragraph after H1")
    guide_steps = models.TextField(blank=True, help_text="How-to guide steps (Markdown/HTML supported)")
    default_target_kb = models.IntegerField(default=350, help_text="Pre-set KB target for specific tools")
    faq_json = models.TextField(blank=True, help_text="JSON format for FAQ: [{'q': '...', 'a': '...'}]")
    is_exam = models.BooleanField(default=False, help_text="Whether this is an exam-specific tool")
    is_tool = models.BooleanField(default=False, help_text="Whether this is a utility-specific tool (e.g., compressor)")
    
    # Specific Requirements
    width_px = models.IntegerField(blank=True, null=True, help_text="Exact width in pixels (overrides mm)")
    height_px = models.IntegerField(blank=True, null=True, help_text="Exact height in pixels (overrides mm)")
    requires_name_overlay = models.BooleanField(default=False, help_text="Requires Name/Date tag on photo")

    # Hierarchy Fields (for Exams)
    exam_country = models.CharField(max_length=100, blank=True, null=True, help_text="e.g. India")
    exam_state = models.CharField(max_length=100, blank=True, null=True, help_text="e.g. Tamil Nadu")
    exam_organization = models.CharField(max_length=100, blank=True, null=True, help_text="e.g. TNPSC")

    def save(self, *args, **kwargs):
        if not self.slug:
            if self.is_exam and self.exam_organization:
                # SEO friendly slug for exams: e.g., tnpsc-group-4-photo-maker
                base_str = f"{self.exam_organization} {self.country} photo maker"
                if self.exam_state:
                     base_str = f"{self.exam_organization} {self.country} {self.exam_state} photo maker"
                self.slug = slugify(base_str)
            else:
                self.slug = slugify(self.country + "-photo-maker")
        else:
            # Force cleanup of manually entered slugs
            self.slug = slugify(self.slug)
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.country

class SiteSettings(models.Model):
    site_name = models.CharField(max_length=200, default="SnapFixer")
    logo = models.ImageField(upload_to='settings/', help_text="Upload your site logo", blank=True, null=True)
    favicon = models.ImageField(upload_to='settings/', help_text="Upload your favicon (ico/png)", blank=True, null=True)

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def save(self, *args, **kwargs):
        # Singleton pattern
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def logo_url(self):
        try:
            return self.logo.url
        except:
            return "/static/img/logo-fallback.png"

    @property
    def favicon_url(self):
        try:
            return self.favicon.url
        except:
            return "/favicon.ico"

    def __str__(self):
        return "Global Site Settings"

class PageMeta(models.Model):
    path = models.CharField(max_length=255, unique=True, help_text="The URL path (e.g., /, /about/, /contact/)")
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    keywords = models.TextField(blank=True)
    
    og_title = models.CharField(max_length=255, blank=True)
    og_description = models.TextField(blank=True)
    og_image = models.ImageField(upload_to='meta/', blank=True, null=True)
    
    twitter_title = models.CharField(max_length=255, blank=True)
    twitter_description = models.TextField(blank=True)
    twitter_image = models.ImageField(upload_to='meta/', blank=True, null=True)
    
    canonical_url = models.CharField(max_length=255, blank=True, help_text="Full absolute URL if different from path")

    class Meta:
        verbose_name = "Page Meta Tag"
        verbose_name_plural = "Page Meta Tags Manager"

    def __str__(self):
        return self.path

class ProcessedPhoto(models.Model):
    rule = models.ForeignKey(CountryRule, on_delete=models.CASCADE)
    original_image = models.ImageField(upload_to='uploads/%Y/%m/%d/')
    processed_image = models.ImageField(upload_to='processed/%Y/%m/%d/', blank=True, null=True)
    status = models.CharField(max_length=20, default='pending') # pending, processing, completed, failed
    error_message = models.TextField(blank=True, null=True)
    task_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class ContactMessage(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.name} ({self.email})"

# Signals for automatic file cleanup
from django.db.models.signals import post_delete
from django.dispatch import receiver

@receiver(post_delete, sender=ProcessedPhoto)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding ProcessedPhoto object is deleted.
    """
    if instance.original_image:
        if os.path.isfile(instance.original_image.path):
            os.remove(instance.original_image.path)

    if instance.processed_image:
        if os.path.isfile(instance.processed_image.path):
            os.remove(instance.processed_image.path)
