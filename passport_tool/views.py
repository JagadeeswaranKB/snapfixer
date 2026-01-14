from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from .models import CountryRule, ProcessedPhoto, ContactMessage
import time

def tool_view(request, slug):
    from .tasks import process_photo_task
    # 1. Search for rule in database by slug
    rule = CountryRule.objects.filter(slug=slug).first()
    
    if not rule:
        # Fallback: maybe it's a legacy slug? Try case-insensitive or partial
        rule = CountryRule.objects.filter(slug__iexact=slug).first()
        if not rule:
            return redirect('home')

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

    # Fallbacks for meta if DB is empty
    default_title = f"Free {rule.country} Photo Maker – AI Tool Online Now"
    default_desc = f"Create official {rule.country} photos ({rule.width_mm}x{rule.height_mm}mm) online instantly. 100% compliant with latest standards and requirements for 2026 today!"

    context = {
        'country_rule': rule,
        'title': rule.meta_title or default_title,
        'meta_description': rule.meta_description or default_desc,
        'meta_keywords': rule.meta_keywords,
        'og_title': rule.og_title or rule.meta_title or default_title,
        'og_description': rule.og_description or rule.meta_description or default_desc,
        'og_image': rule.og_image,
        'twitter_title': rule.twitter_title or rule.meta_title or default_title,
        'twitter_description': rule.twitter_description or rule.meta_description or default_desc,
        'twitter_image': rule.twitter_image,
        'canonical_url': rule.canonical_url,
        'h1': rule.h1 or f"Free {rule.country} Photo Maker",
        'intro_text': rule.intro_text or f"Create a professional {rule.country} photo online instantly. 100% compliant with official {rule.width_mm}x{rule.height_mm}mm standards.",
        'faqs': faqs,
        'target_kb': rule.default_target_kb or 350,
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
        
        # MIME check (optional)
        try:
            import magic
            mime = magic.Magic(mime=True)
            file_mime = mime.from_buffer(photo.read(2048))
            photo.seek(0)
            if file_mime not in settings.ALLOWED_MIME_TYPES:
                return JsonResponse({
                    'error': 'Invalid file format detected.',
                    'status': 'invalid_mime_type'
                }, status=400)
        except:
            pass
        
        if photo.size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
            return JsonResponse({
                'error': 'File too large.',
                'status': 'file_too_large'
            }, status=400)
        
        try:
            country_rule = CountryRule.objects.get(slug=slug)
        except CountryRule.DoesNotExist:
            return JsonResponse({'error': 'Invalid tool'}, status=400)
        
        processed = ProcessedPhoto.objects.create(
            original_image=photo,
            rule=country_rule
        )
        
        uploads.append(current_time)
        request.session[session_key] = uploads
        
        skip_bg = request.POST.get('skip_bg') == 'true'
        use_original_dimensions = request.POST.get('use_original_dimensions') == 'true'
        is_signature = (country_rule.country == "Signature Resizer")

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
    
    if photo.status == 'completed' and photo.processed_image:
        try:
            with photo.processed_image.open('rb') as f:
                encoded_string = base64.b64encode(f.read()).decode('utf-8')
                processed_url = f"data:image/png;base64,{encoded_string}"
            
            photo.processed_image.delete(save=False)
            photo.delete()
            
            return JsonResponse({
                'status': 'completed',
                'processed_url': processed_url
            })
        except Exception as e:
            return JsonResponse({'status': 'failed', 'error': str(e)})
            
    elif photo.status == 'failed':
        err = photo.error_message
        photo.delete()
        return JsonResponse({'status': 'failed', 'error': err})
        
    return JsonResponse({
        'status': photo.status,
        'processed_url': None
    })

def home(request):
    countries = CountryRule.objects.filter(is_exam=False, is_tool=False).exclude(exam_country="Global").order_by('country')
    custom_rule = CountryRule.objects.filter(slug='custom-size-passport-photo').first()
    return render(request, 'passport_tool/home.html', {
        'countries': countries,
        'custom_rule': custom_rule,
    })

def about(request):
    return render(request, 'about.html')

def contact(request):
    if request.method == 'POST':
        honeypot = request.POST.get('website', '')
        if honeypot: return redirect('contact')
        
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        if name and email and message:
            ContactMessage.objects.create(name=name, email=email, message=message)
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contact')
            
    return render(request, 'contact.html')

def privacy(request):
    return render(request, 'privacy.html')

def terms(request):
    return render(request, 'terms.html')
