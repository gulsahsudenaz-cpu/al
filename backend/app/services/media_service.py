"""
Media Processing Service - Voice, Image, File Processing
"""
import io
import mimetypes
from typing import Optional, Dict, Tuple
try:
    from PIL import Image
except ImportError:
    Image = None
from openai import AsyncOpenAI

from app.config import settings
from app.core.logging import get_logger
from app.services.storage_service import storage_service

logger = get_logger(__name__)

# Initialize OpenAI client
openai_client = None
if settings.OPENAI_API_KEY:
    openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)


class MediaService:
    """Media processing service for voice, image, and file processing"""
    
    def __init__(self):
        self.storage = storage_service
        self.openai_client = openai_client
        self.max_image_size = (2048, 2048)  # Max image dimensions
        self.supported_image_formats = ['JPEG', 'PNG', 'WEBP', 'GIF']
        self.supported_audio_formats = ['mp3', 'mp4', 'mpeg', 'mpga', 'm4a', 'wav', 'webm']
    
    async def process_voice(
        self,
        audio_data: bytes,
        file_name: str,
        language: Optional[str] = None
    ) -> Optional[Dict[str, any]]:
        """
        Process voice message using OpenAI Whisper API
        
        Returns:
            dict with 'text', 'language', 'duration' or None if failed
        """
        if not self.openai_client:
            logger.warning("OpenAI client not initialized, voice processing skipped")
            return None
        
        try:
            # Check file size (25MB limit for Whisper API)
            max_size = 25 * 1024 * 1024  # 25MB
            if len(audio_data) > max_size:
                logger.warning("Audio file too large", size=len(audio_data), max_size=max_size)
                return None
            
            # Create file-like object
            audio_file = io.BytesIO(audio_data)
            audio_file.name = file_name
            
            # Transcribe using Whisper API
            transcript = await self.openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language,  # Optional: specify language (e.g., 'tr' for Turkish, 'en' for English)
                response_format="verbose_json"
            )
            
            result = {
                'text': transcript.text,
                'language': getattr(transcript, 'language', language or 'unknown'),
                'duration': getattr(transcript, 'duration', None)
            }
            
            logger.info("Voice transcription completed", language=result['language'], text_length=len(result['text']))
            return result
        
        except Exception as e:
            logger.error("Failed to process voice", file_name=file_name, error=str(e), exc_info=True)
            return None
    
    async def process_image(
        self,
        image_data: bytes,
        file_name: str,
        resize: bool = True,
        max_size: Tuple[int, int] = None
    ) -> Optional[Dict[str, any]]:
        """
        Process image: resize, validate, extract metadata
        
        Returns:
            dict with 'url', 'width', 'height', 'format', 'size' or None if failed
        """
        if Image is None:
            logger.warning("Pillow not installed, image processing skipped")
            return None
        
        try:
            # Open image
            image = Image.open(io.BytesIO(image_data))
            
            # Get image metadata
            width, height = image.size
            format_name = image.format
            mode = image.mode
            
            # Validate format
            if format_name not in self.supported_image_formats:
                logger.warning("Unsupported image format", format=format_name, file_name=file_name)
                return None
            
            # Resize if needed
            max_size = max_size or self.max_image_size
            if resize and (width > max_size[0] or height > max_size[1]):
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
                width, height = image.size
                logger.info("Image resized", original_size=(width, height), new_size=(width, height))
            
            # Convert to RGB if necessary (for JPEG)
            if format_name == 'JPEG' and mode != 'RGB':
                image = image.convert('RGB')
            
            # Save processed image
            processed_image = io.BytesIO()
            image.save(processed_image, format=format_name, quality=85, optimize=True)
            processed_image.seek(0)
            processed_data = processed_image.read()
            
            # Upload to storage
            content_type = mimetypes.guess_type(file_name)[0] or f"image/{format_name.lower()}"
            upload_result = self.storage.upload_file(
                file_content=processed_data,
                file_name=file_name,
                content_type=content_type,
                folder="images"
            )
            
            if not upload_result:
                return None
            
            result = {
                'url': upload_result['url'],
                'key': upload_result['key'],
                'width': width,
                'height': height,
                'format': format_name,
                'size': len(processed_data),
                'original_size': len(image_data)
            }
            
            logger.info("Image processed successfully", file_name=file_name, dimensions=(width, height))
            return result
        
        except Exception as e:
            logger.error("Failed to process image", file_name=file_name, error=str(e), exc_info=True)
            return None
    
    async def process_file(
        self,
        file_data: bytes,
        file_name: str,
        content_type: Optional[str] = None
    ) -> Optional[Dict[str, any]]:
        """
        Process generic file: upload to storage, validate
        
        Returns:
            dict with 'url', 'key', 'size', 'content_type' or None if failed
        """
        try:
            # Guess content type if not provided
            if not content_type:
                content_type = mimetypes.guess_type(file_name)[0] or "application/octet-stream"
            
            # Validate file size
            max_size = settings.MAX_MEDIA_SIZE_MB * 1024 * 1024
            if len(file_data) > max_size:
                logger.warning("File too large", size=len(file_data), max_size=max_size, file_name=file_name)
                return None
            
            # Determine folder based on content type
            folder = "files"
            if content_type.startswith("image/"):
                folder = "images"
            elif content_type.startswith("audio/") or content_type.startswith("video/"):
                folder = "media"
            elif content_type.startswith("text/") or content_type in [
                "application/pdf",
                "application/msword",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ]:
                folder = "documents"
            
            # Upload to storage
            upload_result = self.storage.upload_file(
                file_content=file_data,
                file_name=file_name,
                content_type=content_type,
                folder=folder
            )
            
            if not upload_result:
                return None
            
            result = {
                'url': upload_result['url'],
                'key': upload_result['key'],
                'size': len(file_data),
                'content_type': content_type,
                'original_name': file_name
            }
            
            logger.info("File processed successfully", file_name=file_name, size=len(file_data))
            return result
        
        except Exception as e:
            logger.error("Failed to process file", file_name=file_name, error=str(e), exc_info=True)
            return None
    
    def validate_file(self, file_name: str, file_size: int, content_type: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """
        Validate file before processing
        
        Returns:
            (is_valid, error_message)
        """
        # Check file size
        max_size = settings.MAX_MEDIA_SIZE_MB * 1024 * 1024
        if file_size > max_size:
            return False, f"File size exceeds maximum allowed size ({settings.MAX_MEDIA_SIZE_MB}MB)"
        
        # Check file extension
        file_ext = file_name.rsplit('.', 1)[-1].lower() if '.' in file_name else ''
        
        # Basic validation - can be extended
        dangerous_extensions = ['exe', 'bat', 'cmd', 'sh', 'ps1', 'js', 'vbs']
        if file_ext in dangerous_extensions:
            return False, f"File type not allowed: .{file_ext}"
        
        return True, None


# Global media service instance
media_service = MediaService()

