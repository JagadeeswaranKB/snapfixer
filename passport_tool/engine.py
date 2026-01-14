from PIL import Image, ImageOps, ImageFilter, ImageEnhance, ImageChops
import io
from pillow_heif import register_heif_opener
register_heif_opener()
import os
import numpy as np
import time
from django.core.files.base import ContentFile

# Global session cache to prevent reloading model on every request
SESSIONS = {}

def get_session(model_name):
    from rembg import new_session
    if model_name not in SESSIONS:
        SESSIONS[model_name] = new_session(model_name)
    return SESSIONS[model_name]

def process_image(image_bytes, width_mm, height_mm, bg_color, skip_bg=False, use_original_dimensions=False, is_signature=False):
    """
    Processes an image: handles orientation, removes background (optional), detects face, 
    and crops/resizes with appropriate headroom and zoom levels.
    """
    # 1. Load image and handle EXIF orientation
    try:
        input_image = Image.open(io.BytesIO(image_bytes))
        input_image = ImageOps.exif_transpose(input_image)
    except Exception as e:
        # Fallback for complex formats like some HEIC or corrupted files
        raise Exception(f"Failed to open image: {str(e)}")
    
    # Optimization: Dual Path (Fast AI + High Res Output)
    original_w, original_h = input_image.size
    proxy_size = 1024
    
    # Create Proxy (Always 1024px or smaller) - SKIP FOR SIGNATURES TO PRESERVE DETAIL
    if not is_signature and max(original_w, original_h) > proxy_size:
        proxy_image = input_image.copy()
        proxy_image.thumbnail((proxy_size, proxy_size), Image.Resampling.LANCZOS)
    else:
        proxy_image = input_image.copy()

    # ... (rest of function)

    if not skip_bg:
        if is_signature:
            import cv2
            # OPENCV ADAPTIVE THRESHOLDING: Industry standard for signature processing
            # Use original high-res image logic (proxy is now original size)
            img_array = np.array(input_image.convert("RGB"))
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            # SOFT INK EXTRACTION: Best of both worlds (Sharpness + Natural Fade)
            
            # 1. Enhance Local Contrast (CLAHE) to separate ink from paper
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            enhanced_gray = clahe.apply(gray)
            
            # 2. Stretch Levels (Paper -> White, Ink -> Dark)
            # Find the "paper" level (peak of histogram)
            hist = cv2.calcHist([enhanced_gray], [0], None, [256], [0, 256])
            paper_level = np.argmax(hist)
            
            # Map [0, paper_level] to [0, 255] (Inverted: Ink=255, Paper=0)
            # Anything bright as paper becomes Transparent (0)
            # Anything dark becomes Opaque (255)
            # We add a buffer (offset) to ensure paper is fully transparent
            offset = 15
            limit = max(0, paper_level - offset)
            
            # Create Alpha Map: (paper_level - pixel) * gain
            # Use floating point for calculation
            alpha_float = enhanced_gray.astype(float)
            alpha_float = np.maximum(0, limit - alpha_float) # Invert: Darker becomes larger number
            alpha_float = (alpha_float / limit) * 255.0 # Normalize 0-255
            
            # Apply Gamma to "harden" the ink slightly (make it clearer) but keep soft edges
            # gamma < 1.0 makes faint things darker
            alpha_float = 255 * (alpha_float / 255.0) ** 0.6
            
            alpha_mask = np.clip(alpha_float, 0, 255).astype(np.uint8)
            
            # 3. Detect Ink Color & Auto-Enhance Vibrancy
            mask_bool = alpha_mask > 20 # Only check solid-ish parts
            if mask_bool.any():
                ink_pixels = img_array[mask_bool]
                median_color = np.median(ink_pixels, axis=0).astype(np.uint8)
                
                # Convert to HSV to boost Saturation/Value
                ink_hsv = cv2.cvtColor(np.array([[median_color]]), cv2.COLOR_RGB2HSV)[0][0]
                h, s, v = int(ink_hsv[0]), int(ink_hsv[1]), int(ink_hsv[2])
                
                # 1. Boost Saturation (Make the blue bluer!)
                # If there's some color (s > 20), pump it up. If it's grey, keep it grey.
                if s > 20: 
                    s = min(255, int(s * 2.0)) # Double saturation
                    
                # 2. Darken Value (Make the ink bold/solid)
                # Normalize brightness to ensure good contrast (cap max brightness at 180)
                v = min(v, 180) 
                
                # Convert back to RGB
                ink_color = cv2.cvtColor(np.array([[[h, s, v]]], dtype=np.uint8), cv2.COLOR_HSV2RGB)[0][0]
                
            else:
                ink_color = np.array([0, 0, 0], dtype=np.uint8)

            # 4. Construct Image
            # Solid color base + Soft Alpha Mask
            rgba = np.zeros((img_array.shape[0], img_array.shape[1], 4), dtype=np.uint8)
            rgba[:, :, :3] = ink_color 
            rgba[:, :, 3] = alpha_mask
            
            # Convert back to PIL
            pil_no_bg = Image.fromarray(rgba, 'RGBA')
            
        else:
            # HUMAN PATH: High-Res Masking Pipeline
            model_name = "u2net_human"
            session = get_session(model_name)
            
            # 1. Prepare High-Res Input (Limit to 3200px to prevent OOM, but better than 1024)
            # If image is huge, downscale to a "Ultra High Quality Proxy" 
            hq_proxy_size = 3200
            if max(original_w, original_h) > hq_proxy_size:
                 hq_input = input_image.copy()
                 hq_input.thumbnail((hq_proxy_size, hq_proxy_size), Image.Resampling.LANCZOS)
                 hq_scale_correction = True
            else:
                 hq_input = input_image.copy()
                 hq_scale_correction = False

            # Convert to RGBA for rembg
            hq_input_rgba = hq_input.convert("RGBA")
            buffer = io.BytesIO()
            hq_input_rgba.save(buffer, format="PNG")
            hq_input_bytes = buffer.getvalue()
            
            # 2. Get Mask with Alpha Matting (Slower but much better edges)
            from rembg import remove
            mask_bytes = remove(
                hq_input_bytes,
                session=session,
                only_mask=True,
                alpha_matting=True,
                alpha_matting_foreground_threshold=240,
                alpha_matting_background_threshold=10,
                alpha_matting_erode_size=15 # Increased for higher resolution
            )
            
            hq_mask = Image.open(io.BytesIO(mask_bytes)).convert("L")
            
            # 3. Resize Mask to Original Size if we used a HQ proxy
            if hq_scale_correction or hq_mask.size != (original_w, original_h):
                hq_mask = hq_mask.resize((original_w, original_h), Image.Resampling.LANCZOS)
            
            # 4. Apply to Original Image
            pil_no_bg = input_image.convert("RGBA")
            pil_no_bg.putalpha(hq_mask)

    # 4. Refine alpha mask smoothing (Humans only)
        if not is_signature:
            r, g, b, a = pil_no_bg.split()
            a = a.filter(ImageFilter.GaussianBlur(radius=1.0))
            pil_no_bg = Image.merge("RGBA", (r, g, b, a))
    else:
        # If skipping BG removal, use Original Image
        pil_no_bg = input_image.convert("RGBA")

    # 3. Determine Target Dimensions
    # Calculate bbox based on ACTUAL INK for signatures with extra padding
    bbox = pil_no_bg.getbbox()
    if not bbox:
        bbox = (0, 0, pil_no_bg.width, pil_no_bg.height)
    
    # Add padding to bbox for signatures to prevent cutting letters
    if is_signature and not skip_bg:
        pad_x = int((bbox[2] - bbox[0]) * 0.05)  # 5% horizontal padding
        pad_y = int((bbox[3] - bbox[1]) * 0.05)  # 5% vertical padding
        bbox = (
            max(0, bbox[0] - pad_x),
            max(0, bbox[1] - pad_y),
            min(pil_no_bg.width, bbox[2] + pad_x),
            min(pil_no_bg.height, bbox[3] + pad_y)
        )
    
    subject_w = bbox[2] - bbox[0]
    subject_h = bbox[3] - bbox[1]

    # If skipping background removal OR using original dimensions, bypass all processing
    if skip_bg or use_original_dimensions:
        width_px = pil_no_bg.width
        height_px = pil_no_bg.height
        
        # Bypass scaling/cropping
        scale_factor = 1.0
        paste_x = 0
        paste_y = 0
        scaled_no_bg = pil_no_bg
        
    else:
        # Create target dimensions at 300 DPI
        dpi = 300
        width_px = int((width_mm / 25.4) * dpi)
        height_px = int((height_mm / 25.4) * dpi)
        
        # 5. Face Detection (using RGB version)
        # Only perform face detection if NOT a signature
        faces = []
        if not is_signature:
            import cv2
            # Detect on Proxy for Speed
            cv_img = cv2.cvtColor(np.array(proxy_image.convert("RGB")), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            # Map faces back to High-Res Coordinate Space if needed
            det_scale = pil_no_bg.width / proxy_image.width
            if det_scale != 1.0:
                 faces = [ (int(x*det_scale), int(y*det_scale), int(w*det_scale), int(h*det_scale)) for (x,y,w,h) in faces ]
        
        # 6. Smart Cover Scaling Strategy
        if len(faces) > 0:
            (x, y, w, h) = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)[0]
            scale_factor = (height_px * 0.30) / h
        else:
            # For signatures, use more conservative scaling to prevent cutoff
            target_fill = 0.75 if is_signature else 0.80  # Reduced from 0.85 for more margin
            scale_factor = min(
                (width_px * target_fill) / subject_w,
                (height_px * target_fill) / subject_h
            )
            
        if (subject_w * scale_factor) < width_px:
            # If signature is very wide, it might hit width limit
            if is_signature and (subject_w * scale_factor) > width_px * 0.95:
                 scale_factor = (width_px * 0.95) / subject_w
            else:
                 scale_factor = width_px / subject_w
            
        # Ensure it fits vertically within frame with padding
        if not is_signature:
             dist_to_bottom = pil_no_bg.height - y if len(faces) > 0 else subject_h
             if (dist_to_bottom * scale_factor) < (height_px * 0.85):
                  scale_factor = (height_px * 0.85) / dist_to_bottom
    
        # Calculate new dimensions
        new_w = int(pil_no_bg.width * scale_factor)
        new_h = int(pil_no_bg.height * scale_factor)

        # Use LANCZOS for everything now (Signature needs sharpness)
        resampling_method = Image.Resampling.LANCZOS
        scaled_no_bg = pil_no_bg.resize((new_w, new_h), resampling_method)
        
        # 7. Calculate Positioning
        target_top_margin = height_px * 0.15
        
        if len(faces) > 0:
            scaled_face_center_x = (x + w // 2) * scale_factor
            paste_x = int((width_px / 2) - scaled_face_center_x)
            paste_y = int(target_top_margin - (y * scale_factor))
        else:
            # FOR SIGNATURES: Centering is now based on the PRECISION BBOX of the ink
            scaled_subject_center_x = (bbox[0] + subject_w // 2) * scale_factor
            paste_x = int((width_px / 2) - scaled_subject_center_x)
            
            if is_signature:
                 scaled_subject_center_y = (bbox[1] + subject_h // 2) * scale_factor
                 paste_y = int((height_px / 2) - scaled_subject_center_y)
            else:
                 paste_y = int(target_top_margin - (bbox[1] * scale_factor)) 
    
    # 8. Create Transparent Result (PNG)
    # The background color is now handled by the client-side canvas
    result_canvas = Image.new("RGBA", (width_px, height_px), (0, 0, 0, 0))
    
    # AI Enhancement (Common)
    enhancer_br = ImageEnhance.Brightness(scaled_no_bg)
    scaled_no_bg = enhancer_br.enhance(1.05)
    
    if is_signature:
        # Final auto-enhancement for professional signature quality
        enhancer_ct = ImageEnhance.Contrast(scaled_no_bg)
        scaled_no_bg = enhancer_ct.enhance(1.4)  # Balanced contrast
        enhancer_sh = ImageEnhance.Sharpness(scaled_no_bg)
        scaled_no_bg = enhancer_sh.enhance(1.3)  # Clear edges
    elif not is_signature:
        # Standard Human Enhancement
        enhancer_ct = ImageEnhance.Contrast(scaled_no_bg)
        scaled_no_bg = enhancer_ct.enhance(1.10)
    
    result_canvas.paste(scaled_no_bg, (paste_x, paste_y), scaled_no_bg)

    # 9. Return transparent PNG bytes
    buffer = io.BytesIO()
    result_canvas.save(buffer, format="PNG")
    return buffer.getvalue()

