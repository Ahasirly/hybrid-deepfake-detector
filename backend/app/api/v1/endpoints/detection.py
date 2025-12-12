from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.detection_service import DetectionService
from PIL import Image
from io import BytesIO

router = APIRouter()

# Initialize detection service (singleton)
detection_service = DetectionService()

def compress_image(image_bytes: bytes, max_size_mb: float = 5.0) -> bytes:
    """
    Compress image to reduce file size while maintaining quality

    Args:
        image_bytes: Original image bytes
        max_size_mb: Target max size in MB

    Returns:
        Compressed image bytes
    """
    max_size_bytes = max_size_mb * 1024 * 1024

    # If already small enough, return as is
    if len(image_bytes) <= max_size_bytes:
        return image_bytes

    # Open image
    img = Image.open(BytesIO(image_bytes))

    # Convert RGBA to RGB if needed
    if img.mode == 'RGBA':
        img = img.convert('RGB')

    # Calculate resize ratio to target around 2048px max dimension
    max_dimension = 2048
    if max(img.size) > max_dimension:
        ratio = max_dimension / max(img.size)
        new_size = tuple(int(dim * ratio) for dim in img.size)
        img = img.resize(new_size, Image.Resampling.LANCZOS)

    # Compress with progressive quality reduction
    quality = 85
    output = BytesIO()

    while quality > 20:
        output.seek(0)
        output.truncate(0)
        img.save(output, format='JPEG', quality=quality, optimize=True)

        if len(output.getvalue()) <= max_size_bytes:
            break

        quality -= 5

    compressed_bytes = output.getvalue()
    print(f"[DEBUG] Compressed from {len(image_bytes)/(1024*1024):.2f}MB to {len(compressed_bytes)/(1024*1024):.2f}MB (quality={quality})")

    return compressed_bytes

@router.post("/detect")
async def detect_deepfake(file: UploadFile = File(...)):
    """
    Detect if an uploaded image is a deepfake

    Args:
        file: Uploaded image file (PNG, JPG, JPEG, WEBP)

    Returns:
        Detection results with confidence scores from all models
    """
    print(f"[DEBUG] Received file: {file.filename}, content_type: {file.content_type}")

    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        error_msg = f"Invalid file type: {file.content_type}. Must be an image."
        print(f"[ERROR] {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)

    try:
        # Read image bytes
        image_bytes = await file.read()
        file_size_mb = len(image_bytes) / (1024 * 1024)
        print(f"[DEBUG] File size: {file_size_mb:.2f} MB")

        # Validate file size (20MB limit for upload)
        if len(image_bytes) > 20 * 1024 * 1024:
            raise HTTPException(status_code=400, detail=f"Image size ({file_size_mb:.2f}MB) exceeds 20MB limit")

        # Compress image if needed (target max 5MB for API)
        compressed_bytes = compress_image(image_bytes, max_size_mb=5.0)

        # Run detection
        print(f"[DEBUG] Starting detection...")
        result = detection_service.detect(compressed_bytes)
        print(f"[DEBUG] Detection complete: {result}")

        return result

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Detection error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")
