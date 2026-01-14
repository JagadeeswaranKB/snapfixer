from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from .models import CountryRule, ProcessedPhoto, ContactMessage
import time
from .tasks import process_photo_task

# 100% SEO-Friendly Strategy: Configuration Dictionary
# Legacy SEO_PAGES fallback (All configurations are now database-driven)
SEO_PAGES = {}
def tool_view(request, slug):
    # 1. Search for rule in database by slug (supports custom user-defined slugs)
    try:
        rule = CountryRule.objects.get(slug=slug)
        config = SEO_PAGES.get(slug)
    except CountryRule.DoesNotExist:
        # 2. Fallback to SEO_PAGES if not found in DB
        config = SEO_PAGES.get(slug)
        if not config:
            return redirect('home')
            
        # Create/Get from config to ensure it exists in DB for next time
        rule, _ = CountryRule.objects.get_or_create(
            slug=slug,
            defaults={
                'country': config.get('country', slug.replace('-', ' ').title()),
                'flag_emoji': config.get('flag_emoji', '🏳️'),
                'width_mm': config.get('width_mm', 35),
                'height_mm': config.get('height_mm', 45),
                'bg_color': config.get('bg_color', 'white'),
                'meta_title': config.get('title', ''),
                'meta_description': config.get('description', ''),
                'h1': config.get('h1', ''),
                'is_exam': any(x in slug for x in ['exam', 'neet', 'ssc', 'upsc', 'gate', 'psc', 'cgl']),
                'is_tool': any(x in slug for x in ['-to-', 'compress', 'converter', 'resizer', 'sheet']) and not any(x in slug for x in ['exam', 'neet', 'ssc', 'upsc', 'gate', 'psc', 'cgl'])
            }
        )
    
    # Process FAQ JSON
    import json
    faqs = []
    if rule.faq_json:
        try:
            faqs = json.loads(rule.faq_json)
        except json.JSONDecodeError:
            pass
    
    # Dynamic SEO Content Generation
    from .utils import get_seo_content
    generated_seo_content = get_seo_content(rule)

    # Dynamic SEO Meta Tags
    default_title = f"Make {rule.country} Photo Online - Free Resize & {rule.width_mm}x{rule.height_mm}mm"
    default_desc = f"Create a valid {rule.width_mm}x{rule.height_mm}mm photo for {rule.country} instantly. Official 2026 rules applied. Free AI background removal and download."

    context = {
        'country_rule': rule,
        'title': rule.meta_title or (config.get('title') if config else default_title),
        'meta_description': rule.meta_description or (config.get('description') if config else default_desc),
        'meta_keywords': rule.meta_keywords,
        'og_title': rule.og_title or rule.meta_title,
        'og_description': rule.og_description or rule.meta_description,
        'og_image': rule.og_image,
        'twitter_title': rule.twitter_title or rule.meta_title,
        'twitter_description': rule.twitter_description or rule.meta_description,
        'twitter_image': rule.twitter_image,
        'canonical_url': rule.canonical_url,
        'h1': rule.h1 or (config.get('h1') if config else f"Free {rule.country} Photo Tool"),
        'intro_text': rule.intro_text or (config.get('intro_text') if config else f"Create a professional {rule.country} photo online instantly. 100% compliant with official {rule.width_mm}x{rule.height_mm}mm standards."),
        'faqs': faqs,
        'target_kb': rule.default_target_kb or (config.get('default_target_kb') if config else 350),
        'generated_seo_content': generated_seo_content,
    }
    return render(request, 'passport_tool/tool_detail.html', context)

def image_converter(request):
    try:
        # Use the specific slug we know exists for Custom Size
        rule = CountryRule.objects.get(slug='custom-size-passport-photo')
    except CountryRule.DoesNotExist:
        # Fallback or error handling if the rule is missing
        rule = CountryRule.objects.filter(country="Custom Size").first()
    
    if not rule:
        return redirect('home')
        
    # Dynamic SEO Content Generation
    from .utils import get_seo_content
    generated_seo_content = get_seo_content(rule)

    context = {
        'country_rule': rule,
        'title': rule.meta_title or "Online Image Converter & Resizer | SnapFixer",
        'meta_description': rule.meta_description or "Convert and resize images to any dimension or file size online. Supports JPG, PNG, WEBP, and BMP. Free, fast, and secure.",
        'meta_keywords': rule.meta_keywords,
        'og_title': rule.og_title or rule.meta_title,
        'og_description': rule.og_description or rule.meta_description,
        'og_image': rule.og_image,
        'twitter_title': rule.twitter_title or rule.meta_title,
        'twitter_description': rule.twitter_description or rule.meta_description,
        'twitter_image': rule.twitter_image,
        'canonical_url': rule.canonical_url,
        'h1': rule.h1 or "Online Image Converter & Resizer",
        'intro_text': rule.intro_text or "Need a custom image size? Use our advanced resizer to convert formats and reach specific KB targets instantly.",
        'generated_seo_content': generated_seo_content,
        'is_tool': True
    }
    
    return render(request, 'passport_tool/image_converter.html', context)

def upload_photo(request, slug):
    if request.method == 'POST' and request.FILES.get('photo'):
        # Rate limiting - max 20 uploads per 30 minutes per IP
        ip_address = request.META.get('REMOTE_ADDR', '')
        session_key = f'photo_uploads_{ip_address}'
        
        # Get upload timestamps from session
        uploads = request.session.get(session_key, [])
        current_time = time.time()
        
        # Remove uploads older than 30 minutes (1800 seconds)
        uploads = [ts for ts in uploads if current_time - ts < 1800]
        
        if len(uploads) >= 20:
            return JsonResponse({
                'error': 'Too many uploads. Please try again later.',
                'status': 'rate_limited'
            }, status=429)
        
        photo = request.FILES['photo']
        
        # File validation - check extension
        import os
        from django.conf import settings
        
        file_ext = os.path.splitext(photo.name)[1].lower()
        if file_ext not in settings.ALLOWED_UPLOAD_EXTENSIONS:
            return JsonResponse({
                'error': f'Invalid file type. Allowed types: {", ".join(settings.ALLOWED_UPLOAD_EXTENSIONS)}',
                'status': 'invalid_file_type'
            }, status=400)
        
        # File validation - check MIME type (optional if python-magic not installed)
        try:
            import magic
            mime = magic.Magic(mime=True)
            file_mime = mime.from_buffer(photo.read(2048))
            photo.seek(0)  # Reset file pointer
            
            if file_mime not in settings.ALLOWED_MIME_TYPES:
                return JsonResponse({
                    'error': 'Invalid file format detected.',
                    'status': 'invalid_mime_type'
                }, status=400)
        except (ImportError, Exception):
            # If python-magic is not available or fails, skip MIME check
            # Extension validation is still enforced above
            pass
        
        # File validation - check file size (additional check)
        if photo.size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
            return JsonResponse({
                'error': f'File too large. Maximum size: {settings.FILE_UPLOAD_MAX_MEMORY_SIZE / (1024*1024):.0f}MB',
                'status': 'file_too_large'
            }, status=400)
        
        try:
            country_rule = CountryRule.objects.get(slug=slug)
        except CountryRule.DoesNotExist:
            return JsonResponse({'error': 'Invalid country'}, status=400)
        
        # Save the photo
        processed = ProcessedPhoto.objects.create(
            original_image=photo, # Changed from original_photo to original_image to match model field
            rule=country_rule # Changed from country_rule to rule to match model field
        )
        
        # Update rate limiting
        uploads.append(current_time)
        request.session[session_key] = uploads
        
        # Check for skip_bg parameter
        skip_bg = request.POST.get('skip_bg') == 'true'
        use_original_dimensions = request.POST.get('use_original_dimensions') == 'true'
        
        # Determine if this is a signature tool request
        is_signature = (country_rule.country == "Signature Resizer")

        # Trigger async task
        task = process_photo_task.delay(
            processed.id, 
            skip_bg=skip_bg, 
            use_original_dimensions=use_original_dimensions,
            is_signature=is_signature
        )
        processed.task_id = task.id
        processed.save()
        
        return JsonResponse({
            'photo_id': processed.id,
            'status': 'processing',
            'task_id': task.id
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

import base64

def check_status(request, photo_id):
    photo = get_object_or_404(ProcessedPhoto, id=photo_id)
    
    if photo.status == 'completed':
        # 1. Read the processed image
        with photo.processed_image.open('rb') as f:
            encoded_string = base64.b64encode(f.read()).decode('utf-8')
            processed_url = f"data:image/png;base64,{encoded_string}"
        
        # 2. Privacy: Delete the file and the record instantly
        photo.processed_image.delete(save=False)
        photo.delete()  # This deletes the DB record
        
        return JsonResponse({
            'status': 'completed',
            'processed_url': processed_url
        })
    elif photo.status == 'failed':
        # Clean up database record on failure
        photo.delete()
        return JsonResponse({'status': 'failed', 'error': photo.error_message})
        
    return JsonResponse({
        'status': photo.status,
        'processed_url': None
    })

def home(request):
    countries = CountryRule.objects.filter(is_exam=False, is_tool=False).exclude(country="Custom Size").order_by('country')
    custom_rule = CountryRule.objects.filter(country="Custom Size").first()
    return render(request, 'passport_tool/home.html', {
        'countries': countries,
        'custom_rule': custom_rule,
    })

def about(request):
    return render(request, 'about.html')

def contact(request):
    if request.method == 'POST':
        # Honeypot check - if filled, it's a bot
        honeypot = request.POST.get('website', '')
        if honeypot:
            # Silently reject spam without error message
            return redirect('contact')
        
        # Time-based check - reject if submitted too quickly (< 3 seconds)
        form_timestamp = request.POST.get('form_timestamp', '')
        if form_timestamp:
            try:
                render_time = int(form_timestamp)
                current_time = int(time.time() * 1000)  # milliseconds
                time_diff = (current_time - render_time) / 1000  # convert to seconds
                
                if time_diff < 3:  # Submitted in less than 3 seconds
                    messages.error(request, 'Please take your time to fill out the form.')
                    return redirect('contact')
            except (ValueError, TypeError):
                pass  # Invalid timestamp, continue with submission
        
        # Rate limiting - max 3 submissions per hour per IP
        ip_address = request.META.get('REMOTE_ADDR', '')
        session_key = f'contact_submissions_{ip_address}'
        
        # Get submission timestamps from session
        submissions = request.session.get(session_key, [])
        current_time = time.time()
        
        # Remove submissions older than 1 hour
        submissions = [ts for ts in submissions if current_time - ts < 3600]
        
        if len(submissions) >= 3:
            messages.error(request, 'Too many submissions. Please try again later.')
            return redirect('contact')
        
        # Process the form
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        if name and email and message:
            ContactMessage.objects.create(name=name, email=email, message=message)
            
            # Update rate limiting
            submissions.append(current_time)
            request.session[session_key] = submissions
            
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contact')
            
    return render(request, 'contact.html')

def privacy(request):
    return render(request, 'privacy.html')

def terms(request):
    return render(request, 'terms.html')
