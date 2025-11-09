"""
Media API Routes - File Upload, Voice Processing, Image Processing
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
import uuid

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.logging import get_logger
from app.services.media_service import media_service
from app.services.storage_service import storage_service
from app.config import settings

router = APIRouter()
logger = get_logger(__name__)


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    chat_id: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload file (image, document, audio, video)
    
    Supports:
    - Images: JPEG, PNG, WEBP, GIF (auto-resize)
    - Documents: PDF, DOC, DOCX, TXT
    - Audio: MP3, WAV, M4A (voice transcription available)
    - Video: MP4, WEBM
    """
    try:
        # Validate file
        file_content = await file.read()
        file_size = len(file_content)
        
        is_valid, error_message = media_service.validate_file(
            file_name=file.filename or "unknown",
            file_size=file_size,
            content_type=file.content_type
        )
        
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_message)
        
        # Process file based on content type
        content_type = file.content_type or "application/octet-stream"
        file_name = file.filename or f"file_{uuid.uuid4()}"
        
        if content_type.startswith("image/"):
            # Process image
            result = await media_service.process_image(
                image_data=file_content,
                file_name=file_name,
                resize=True
            )
        elif content_type.startswith("audio/"):
            # Process audio (voice transcription)
            result = await media_service.process_file(
                file_data=file_content,
                file_name=file_name,
                content_type=content_type
            )
            
            # Optionally transcribe voice
            if content_type in ["audio/mpeg", "audio/mp4", "audio/wav", "audio/webm", "audio/m4a"]:
                transcription = await media_service.process_voice(
                    audio_data=file_content,
                    file_name=file_name
                )
                if transcription:
                    result['transcription'] = transcription
        else:
            # Process generic file
            result = await media_service.process_file(
                file_data=file_content,
                file_name=file_name,
                content_type=content_type
            )
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to process file")
        
        logger.info("File uploaded successfully", file_name=file_name, size=file_size, chat_id=chat_id)
        
        return {
            "success": True,
            "file": {
                "url": result.get("url"),
                "key": result.get("key"),
                "size": result.get("size"),
                "content_type": result.get("content_type"),
                "original_name": result.get("original_name", file_name),
                "width": result.get("width"),
                "height": result.get("height"),
                "transcription": result.get("transcription")
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error uploading file", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to upload file")


@router.post("/upload/voice")
async def upload_voice(
    file: UploadFile = File(...),
    language: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload voice message and transcribe using Whisper API
    
    Supported formats: MP3, WAV, M4A, WEBM
    Language: Optional language code (e.g., 'tr' for Turkish, 'en' for English)
    """
    try:
        # Read file
        file_content = await file.read()
        file_name = file.filename or "voice.mp3"
        
        # Validate file size (25MB limit for Whisper API)
        max_size = 25 * 1024 * 1024  # 25MB
        if len(file_content) > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum allowed size (25MB)"
            )
        
        # Process voice
        transcription = await media_service.process_voice(
            audio_data=file_content,
            file_name=file_name,
            language=language
        )
        
        if not transcription:
            raise HTTPException(status_code=500, detail="Failed to transcribe voice")
        
        # Upload audio file to storage
        upload_result = await media_service.process_file(
            file_data=file_content,
            file_name=file_name,
            content_type=file.content_type or "audio/mpeg"
        )
        
        logger.info("Voice transcribed successfully", language=transcription.get("language"))
        
        return {
            "success": True,
            "transcription": {
                "text": transcription.get("text"),
                "language": transcription.get("language"),
                "duration": transcription.get("duration")
            },
            "file": upload_result
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error processing voice", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to process voice")


@router.post("/upload/image")
async def upload_image(
    file: UploadFile = File(...),
    resize: bool = Form(True),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload image and process (resize, optimize)
    
    Supported formats: JPEG, PNG, WEBP, GIF
    Auto-resize to max 2048x2048 if resize=True
    """
    try:
        # Read file
        file_content = await file.read()
        file_name = file.filename or "image.jpg"
        
        # Validate content type
        content_type = file.content_type or "image/jpeg"
        if not content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Process image
        result = await media_service.process_image(
            image_data=file_content,
            file_name=file_name,
            resize=resize
        )
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to process image")
        
        logger.info("Image uploaded successfully", file_name=file_name, dimensions=(result.get("width"), result.get("height")))
        
        return {
            "success": True,
            "image": {
                "url": result.get("url"),
                "key": result.get("key"),
                "width": result.get("width"),
                "height": result.get("height"),
                "format": result.get("format"),
                "size": result.get("size"),
                "original_size": result.get("original_size")
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error uploading image", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to upload image")


@router.delete("/files/{file_key}")
async def delete_file(
    file_key: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete uploaded file"""
    try:
        # Check if user has permission (admin only)
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Delete file
        success = storage_service.delete_file(file_key)
        
        if not success:
            raise HTTPException(status_code=404, detail="File not found")
        
        logger.info("File deleted successfully", file_key=file_key)
        
        return {"success": True, "message": "File deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error deleting file", file_key=file_key, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete file")


@router.get("/files/{file_key}/url")
async def get_file_url(
    file_key: str,
    expires_in: int = 3600,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get presigned URL for file"""
    try:
        url = storage_service.get_file_url(file_key, expires_in=expires_in)
        
        if not url:
            raise HTTPException(status_code=404, detail="File not found")
        
        return {"url": url, "expires_in": expires_in}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting file URL", file_key=file_key, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get file URL")

