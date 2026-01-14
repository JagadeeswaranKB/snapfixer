from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field


class BlogCategory(models.Model):
    """Blog categories for organizing posts"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Blog Categories"
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class BlogPost(models.Model):
    """Main blog post model with SEO fields"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]
    
    # Basic fields
    title = models.CharField(max_length=200, help_text="Blog post title")
    slug = models.SlugField(max_length=200, unique=True, blank=True, help_text="URL-friendly version of title")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    
    # Content
    content = CKEditor5Field(config_name='blog', help_text="Main blog content (supports HTML)")
    excerpt = models.TextField(max_length=300, blank=True, help_text="Short summary for previews")
    featured_image = models.ImageField(upload_to='blog/images/', blank=True, null=True)
    
    # SEO fields
    meta_title = models.CharField(max_length=60, blank=True, help_text="SEO title (60 chars max)")
    meta_description = models.CharField(max_length=160, blank=True, help_text="SEO description (160 chars max)")
    meta_keywords = models.CharField(max_length=255, blank=True, help_text="Comma-separated keywords")
    
    # Open Graph / Social Media
    og_title = models.CharField(max_length=200, blank=True, help_text="Open Graph title")
    og_description = models.TextField(blank=True, help_text="Open Graph description")
    og_image = models.ImageField(upload_to='blog/og/', blank=True, null=True, help_text="Social media share image")
    
    # Twitter Card
    twitter_title = models.CharField(max_length=200, blank=True, help_text="Twitter title")
    twitter_description = models.TextField(blank=True, help_text="Twitter description")
    twitter_image = models.ImageField(upload_to='blog/twitter/', blank=True, null=True, help_text="Twitter share image")
    
    canonical_url = models.CharField(max_length=255, blank=True, help_text="Full absolute URL if different from path")
    
    # Status and dates
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Analytics
    view_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-published_at', '-created_at']
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"
    
    def save(self, *args, **kwargs):
        # Auto-generate slug from title
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Auto-fill SEO fields if empty
        if not self.meta_title:
            self.meta_title = self.title[:60]
        if not self.meta_description and self.excerpt:
            self.meta_description = self.excerpt[:160]
        if not self.og_title:
            self.og_title = self.meta_title
        if not self.og_description:
            self.og_description = self.meta_description
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('blog_detail', kwargs={'slug': self.slug})
    
    def __str__(self):
        return self.title
    
    @property
    def reading_time(self):
        """Calculate estimated reading time in minutes"""
        words = len(self.content.split())
        return max(1, round(words / 200))  # Average reading speed: 200 words/min
