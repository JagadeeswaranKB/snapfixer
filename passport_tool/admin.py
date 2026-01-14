from django.contrib import admin
from .models import CountryRule, ContactMessage, SiteSettings, PageMeta

@admin.register(CountryRule)
class CountryRuleAdmin(admin.ModelAdmin):
    list_display = ('country', 'slug', 'is_tool', 'is_exam')
    search_fields = ('country', 'slug')
    list_filter = ('is_tool', 'is_exam')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('country', 'slug', 'flag_emoji', 'width_mm', 'height_mm', 'bg_color')
        }),
        ('Specific Requirements', {
            'fields': ('width_px', 'height_px', 'requires_name_overlay', 'default_target_kb')
        }),
        ('Hierarchy (Exams Only)', {
            'fields': ('is_exam', 'is_tool', 'exam_country', 'exam_state', 'exam_organization')
        }),
        ('SEO Content', {
            'fields': ('h1', 'intro_text', 'content_body', 'guide_steps', 'faq_json')
        }),
        ('Meta Tags', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords', 'canonical_url')
        }),
        ('Social Media (Open Graph)', {
            'fields': ('og_title', 'og_description', 'og_image')
        }),
        ('Social Media (Twitter)', {
            'fields': ('twitter_title', 'twitter_description', 'twitter_image')
        }),
    )

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('created_at',)

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(PageMeta)
class PageMetaAdmin(admin.ModelAdmin):
    list_display = ('path', 'title')
    search_fields = ('path', 'title', 'description')
    list_per_page = 200
