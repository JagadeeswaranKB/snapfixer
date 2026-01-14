
def get_seo_content(item):
    """
    Generates dynamic, high-quality SEO content for tool pages.
    """
    name = item.country
    width = item.width_mm
    height = item.height_mm
    bg = item.bg_color or "white"
    
    # Check tool type
    is_signature = "signature" in name.lower()
    # Format converters have "to" in name (e.g., "BMP to JPG", "WebP to PNG")
    is_converter = (
        "converter" in name.lower() or 
        "compress" in name.lower() or 
        "resize" in name.lower() or 
        "custom" in name.lower() or
        " to " in name.lower() or  # Format conversion pages
        "webp" in name.lower() or
        "bmp" in name.lower() or
        "png" in name.lower() or
        "jpg" in name.lower()
    )
    
    # 1. Requirements Section
    if is_converter:
        # Generic image tool - no photo-specific requirements
        requirements = f"""
    <div class="mb-8">
        <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-4">Image Requirements</h3>
        <p class="text-gray-700 dark:text-gray-300 mb-4 leading-relaxed">Get the perfect image size and format for any purpose:</p>
        <ul class="space-y-3 text-gray-700 dark:text-gray-300">
            <li class="flex items-start gap-3">
                <i class="fas fa-check-circle text-green-500 mt-1"></i>
                <span><strong class="text-gray-900 dark:text-white">Flexible Sizing:</strong> Resize to any dimensions you need - {width}mm × {height}mm or custom sizes.</span>
            </li>
            <li class="flex items-start gap-3">
                <i class="fas fa-check-circle text-green-500 mt-1"></i>
                <span><strong class="text-gray-900 dark:text-white">Format Options:</strong> Convert between JPG, PNG, WEBP, BMP, and other formats.</span>
            </li>
            <li class="flex items-start gap-3">
                <i class="fas fa-check-circle text-green-500 mt-1"></i>
                <span><strong class="text-gray-900 dark:text-white">File Size Control:</strong> Compress images to specific file sizes (e.g., 20KB, 50KB, 100KB).</span>
            </li>
            <li class="flex items-start gap-3">
                <i class="fas fa-check-circle text-green-500 mt-1"></i>
                <span><strong class="text-gray-900 dark:text-white">High Quality:</strong> Maintains image quality while optimizing file size.</span>
            </li>
            <li class="flex items-start gap-3">
                <i class="fas fa-check-circle text-green-500 mt-1"></i>
                <span><strong class="text-gray-900 dark:text-white">Background Removal:</strong> Optional AI-powered background removal for any image.</span>
            </li>
        </ul>
    </div>
    """
    elif is_signature:
        requirements = f"""
    <div class="mb-8">
        <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-4">Official {name} Requirements</h3>
        <p class="text-gray-700 dark:text-gray-300 mb-4 leading-relaxed">To ensure your {name} is accepted, it must strictly adhere to these official standards:</p>
        <ul class="space-y-3 text-gray-700 dark:text-gray-300">
            <li class="flex items-start gap-3">
                <i class="fas fa-check-circle text-green-500 mt-1"></i>
                <span><strong class="text-gray-900 dark:text-white">Dimensions:</strong> Exactly {width}mm width × {height}mm height.</span>
            </li>
            <li class="flex items-start gap-3">
                <i class="fas fa-check-circle text-green-500 mt-1"></i>
                <span><strong class="text-gray-900 dark:text-white">Background:</strong> A plain, uniform {bg} background with no shadows or patterns.</span>
            </li>
            <li class="flex items-start gap-3">
                <i class="fas fa-check-circle text-green-500 mt-1"></i>
                <span><strong class="text-gray-900 dark:text-white">Clarity:</strong> Signature must be clear, legible, and in dark ink (black or blue).</span>
            </li>
            <li class="flex items-start gap-3">
                <i class="fas fa-check-circle text-green-500 mt-1"></i>
                <span><strong class="text-gray-900 dark:text-white">Quality:</strong> High resolution with no blur or pixelation. SnapFixer ensures 300 DPI output.</span>
            </li>
            <li class="flex items-start gap-3">
                <i class="fas fa-check-circle text-green-500 mt-1"></i>
                <span><strong class="text-gray-900 dark:text-white">Format:</strong> Must be a scanned or photographed signature, not digitally created.</span>
            </li>
        </ul>
    </div>
    """
    else:
        # Passport/ID/Exam photos
        requirements = f"""
    <div class="mb-8">
        <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-4">Official {name} Photo Requirements</h3>
        <p class="text-gray-700 dark:text-gray-300 mb-4 leading-relaxed">To ensure your {name} application is successful, your photo must strictly adhere to these official standards:</p>
        <ul class="space-y-3 text-gray-700 dark:text-gray-300">
            <li class="flex items-start gap-3">
                <i class="fas fa-check-circle text-green-500 mt-1"></i>
                <span><strong class="text-gray-900 dark:text-white">Dimensions:</strong> Exactly {width}mm width × {height}mm height.</span>
            </li>
            <li class="flex items-start gap-3">
                <i class="fas fa-check-circle text-green-500 mt-1"></i>
                <span><strong class="text-gray-900 dark:text-white">Background:</strong> A plain, uniform {bg} background with no shadows or patterns.</span>
            </li>
            <li class="flex items-start gap-3">
                <i class="fas fa-check-circle text-green-500 mt-1"></i>
                <span><strong class="text-gray-900 dark:text-white">Head Size:</strong> The head should occupy between 70% to 80% of the total photo height.</span>
            </li>
            <li class="flex items-start gap-3">
                <i class="fas fa-check-circle text-green-500 mt-1"></i>
                <span><strong class="text-gray-900 dark:text-white">Expression:</strong> Keep a neutral facial expression with both eyes open and looking directly at the camera.</span>
            </li>
            <li class="flex items-start gap-3">
                <i class="fas fa-check-circle text-green-500 mt-1"></i>
                <span><strong class="text-gray-900 dark:text-white">Recency:</strong> The photo must have been taken within the last 6 months to reflect your current appearance.</span>
            </li>
        </ul>
    </div>
    """
    
    # 2. Rejection Reasons
    if is_converter:
        rejections = f"""
    <div class="mb-8">
        <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-4">Common Image Issues</h3>
        <p class="text-gray-700 dark:text-gray-300 mb-4 leading-relaxed">Avoid these common image problems:</p>
        <ul class="space-y-3 text-gray-700 dark:text-gray-300">
            <li class="flex items-start gap-3">
                <i class="fas fa-times-circle text-red-500 mt-1"></i>
                <span><strong class="text-gray-900 dark:text-white">Wrong Dimensions:</strong> Image doesn't meet size requirements for your application.</span>
            </li>
            <li class="flex items-start gap-3">
                <i class="fas fa-times-circle text-red-500 mt-1"></i>
                <span><strong class="text-gray-900 dark:text-white">File Too Large:</strong> Image exceeds maximum file size limits.</span>
            </li>
            <li class="flex items-start gap-3">
                <i class="fas fa-times-circle text-red-500 mt-1"></i>
                <span><strong class="text-gray-900 dark:text-white">Wrong Format:</strong> Application requires a specific format (JPG, PNG, etc.).</span>
            </li>
            <li class="flex items-start gap-3">
                <i class="fas fa-times-circle text-red-500 mt-1"></i>
                <span><strong class="text-gray-900 dark:text-white">Low Quality:</strong> Image is blurry or pixelated after compression.</span>
            </li>
        </ul>
    </div>
    """
    elif is_signature:
        rejections = f"""
    <div class="mb-8">
        <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-4">Common Reasons for {name} Rejection</h3>
        <p class="text-gray-700 dark:text-gray-300 mb-4 leading-relaxed">Many applications are delayed due to signature errors. Avoid these common pitfalls:</p>
        <ul class="space-y-3 text-gray-700 dark:text-gray-300">
            <li class="flex items-start gap-3">
                <i class="fas fa-times-circle text-red-500 mt-1"></i>
                <span><strong class="text-gray-900 dark:text-white">Incorrect Sizing:</strong> Even a few millimeters off can lead to automatic rejection.</span>
            </li>
            <li class="flex items-start gap-3">
                <i class="fas fa-times-circle text-red-500 mt-1"></i>
                <span><strong class="text-gray-900 dark:text-white">Poor Quality:</strong> Blurry, pixelated, or low-resolution signatures will not be accepted.</span>
            </li>
            <li class="flex items-start gap-3">
                <i class="fas fa-times-circle text-red-500 mt-1"></i>
                <span><strong class="text-gray-900 dark:text-white">Incomplete Signature:</strong> Parts of the signature cut off or missing.</span>
            </li>
            <li class="flex items-start gap-3">
                <i class="fas fa-times-circle text-red-500 mt-1"></i>
                <span><strong class="text-gray-900 dark:text-white">Wrong Background:</strong> Non-{bg} background or visible shadows.</span>
            </li>
        </ul>
    </div>
    """
    else:
        rejections = f"""
    <div class="mb-8">
        <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-4">Common Reasons for {name} Photo Rejection</h3>
        <p class="text-gray-700 dark:text-gray-300 mb-4 leading-relaxed">Many {name} applications are delayed due to minor photo errors. Avoid these common pitfalls:</p>
        <ul class="space-y-3 text-gray-700 dark:text-gray-300">
            <li class="flex items-start gap-3">
                <i class="fas fa-times-circle text-red-500 mt-1"></i>
                <span><strong class="text-gray-900 dark:text-white">Incorrect Sizing:</strong> Even a few millimeters off can lead to automatic rejection by government scanners.</span>
            </li>
            <li class="flex items-start gap-3">
                <i class="fas fa-times-circle text-red-500 mt-1"></i>
                <span><strong class="text-gray-900 dark:text-white">Poor Background:</strong> Shadows behind the head or a non-compliant "{bg}" background are frequent issues.</span>
            </li>
            <li class="flex items-start gap-3">
                <i class="fas fa-times-circle text-red-500 mt-1"></i>
                <span><strong class="text-gray-900 dark:text-white">Facial Obstructions:</strong> Large glasses frames, hair covering the eyes, or heavy jewelry can invalidate your photo.</span>
            </li>
            <li class="flex items-start gap-3">
                <i class="fas fa-times-circle text-red-500 mt-1"></i>
                <span><strong class="text-gray-900 dark:text-white">Low Resolution:</strong> Photos that are blurry or pixelated will not be accepted. SnapFixer ensures 300 DPI high-quality output.</span>
            </li>
        </ul>
    </div>
    """
    
    # 3. How-to Guide
    if is_converter:
        guide = f"""
    <div class="mb-8">
        <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-4">How to Use Image Converter in 3 Simple Steps</h3>
        <p class="text-gray-700 dark:text-gray-300 mb-4 leading-relaxed">Using SnapFixer's image converter is quick and easy:</p>
        <ol class="space-y-4 text-gray-700 dark:text-gray-300">
            <li class="flex items-start gap-3">
                <span class="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-sm">1</span>
                <span><strong class="text-gray-900 dark:text-white">Upload:</strong> Choose any image from your device. Supports JPG, PNG, WEBP, BMP, HEIC, and more.</span>
            </li>
            <li class="flex items-start gap-3">
                <span class="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-sm">2</span>
                <span><strong class="text-gray-900 dark:text-white">Customize:</strong> Set your desired dimensions, format, and file size. Optionally remove background.</span>
            </li>
            <li class="flex items-start gap-3">
                <span class="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-sm">3</span>
                <span><strong class="text-gray-900 dark:text-white">Download:</strong> Get your optimized image instantly in high quality.</span>
            </li>
        </ol>
    </div>
    """
    elif is_signature:
        guide = f"""
    <div class="mb-8">
        <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-4">How to Create {name} in 3 Simple Steps</h3>
        <p class="text-gray-700 dark:text-gray-300 mb-4 leading-relaxed">Using SnapFixer's AI-powered {name} tool is the fastest way to get a compliant signature:</p>
        <ol class="space-y-4 text-gray-700 dark:text-gray-300">
            <li class="flex items-start gap-3">
                <span class="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-sm">1</span>
                <span><strong class="text-gray-900 dark:text-white">Upload:</strong> Upload a photo or scan of your signature. Our AI automatically removes the background and isolates the signature.</span>
            </li>
            <li class="flex items-start gap-3">
                <span class="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-sm">2</span>
                <span><strong class="text-gray-900 dark:text-white">Adjust:</strong> The signature is automatically resized to {width}mm × {height}mm with perfect centering.</span>
            </li>
            <li class="flex items-start gap-3">
                <span class="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-sm">3</span>
                <span><strong class="text-gray-900 dark:text-white">Download:</strong> Export your signature in high-res JPG or PNG format, ready for your application.</span>
            </li>
        </ol>
    </div>
    """
    else:
        guide = f"""
    <div class="mb-8">
        <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-4">How to Resize for {name} in 3 Simple Steps</h3>
        <p class="text-gray-700 dark:text-gray-300 mb-4 leading-relaxed">Using SnapFixer's AI-powered {name} photo maker is the fastest way to get a compliant image:</p>
        <ol class="space-y-4 text-gray-700 dark:text-gray-300">
            <li class="flex items-start gap-3">
                <span class="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-sm">1</span>
                <span><strong class="text-gray-900 dark:text-white">Upload:</strong> Choose your best selfie. Our AI automatically removes the old background and replaces it with "{bg}".</span>
            </li>
            <li class="flex items-start gap-3">
                <span class="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-sm">2</span>
                <span><strong class="text-gray-900 dark:text-white">Align:</strong> Use our "Official Grid" overlay to position your face perfectly between the eye and chin lines.</span>
            </li>
            <li class="flex items-start gap-3">
                <span class="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-sm">3</span>
                <span><strong class="text-gray-900 dark:text-white">Download:</strong> Export your photo in high-res JPG or PNG. You can also download a 4×6" print sheet with multiple copies.</span>
            </li>
        </ol>
    </div>
    """
    
    return requirements + rejections + guide
