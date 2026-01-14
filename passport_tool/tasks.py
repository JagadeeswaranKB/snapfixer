from celery import shared_task
from .models import ProcessedPhoto
from .engine import process_image
from django.core.files.base import ContentFile
import os

@shared_task
def process_photo_task(photo_id, **kwargs):
    try:
        photo = ProcessedPhoto.objects.get(id=photo_id)
        photo.status = 'processing'
        photo.save()
        
        # Read image bytes
        with photo.original_image.open('rb') as f:
            image_bytes = f.read()
            
        # Process
        skip_bg = kwargs.get('skip_bg', False)
        use_original_dimensions = kwargs.get('use_original_dimensions', False)
        is_signature = kwargs.get('is_signature', False)
        
        processed_bytes = process_image(
            image_bytes, 
            photo.rule.width_mm, 
            photo.rule.height_mm, 
            photo.rule.bg_color,
            skip_bg=skip_bg,
            use_original_dimensions=use_original_dimensions,
            is_signature=is_signature
        )
        
        # Save processed image
        filename = f"processed_{os.path.basename(photo.original_image.name)}"
        if not filename.endswith('.png'):
             filename = filename.rsplit('.', 1)[0] + '.png'
             
        photo.processed_image.save(filename, ContentFile(processed_bytes), save=False)
        photo.status = 'completed'
        
        # Privacy: Delete original image file after processing
        photo.original_image.delete(save=False)
        photo.save()
        
        return True
    except Exception as e:
        import sys
        import traceback
        error_msg = str(e)
        traceback.print_exc(file=sys.stderr) # Log to Docker logs
        
        if 'photo' in locals():
            # Ensure cleanup on failure too
            if photo.original_image:
                photo.original_image.delete(save=False)
            photo.status = 'failed'
            photo.error_message = error_msg
            photo.save()
        return str(e)

from django.utils import timezone
from datetime import timedelta

@shared_task
def cleanup_old_photos():
    """
    Deletes ProcessedPhoto records older than 1 hour.
    The post_delete signals will handle deleting the files.
    """
    one_hour_ago = timezone.now() - timedelta(hours=1)
    old_photos = ProcessedPhoto.objects.filter(created_at__lt=one_hour_ago)
    count = old_photos.count()
    old_photos.delete()  # This triggers the post_delete signal
    return f"Deleted {count} old photo records."
