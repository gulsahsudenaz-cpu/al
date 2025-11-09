"""
Storage Service - S3/MinIO Integration
"""
import os
import uuid
from typing import Optional, BinaryIO
from datetime import datetime, timedelta
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config

from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class StorageService:
    """Storage service for S3/MinIO"""
    
    def __init__(self):
        self.s3_client = None
        self.bucket_name = settings.S3_BUCKET_NAME
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize S3 client"""
        if not settings.S3_ENDPOINT_URL or not settings.S3_ACCESS_KEY or not settings.S3_SECRET_KEY:
            logger.warning("S3 credentials not configured. File uploads will be disabled.")
            return
        
        try:
            s3_config = Config(
                signature_version='s3v4',
                retries={'max_attempts': 3, 'mode': 'standard'}
            )
            
            if settings.USE_MINIO:
                # MinIO configuration
                self.s3_client = boto3.client(
                    's3',
                    endpoint_url=settings.S3_ENDPOINT_URL,
                    aws_access_key_id=settings.S3_ACCESS_KEY,
                    aws_secret_access_key=settings.S3_SECRET_KEY,
                    config=s3_config,
                    use_ssl=False
                )
            else:
                # AWS S3 configuration
                self.s3_client = boto3.client(
                    's3',
                    endpoint_url=settings.S3_ENDPOINT_URL,
                    aws_access_key_id=settings.S3_ACCESS_KEY,
                    aws_secret_access_key=settings.S3_SECRET_KEY,
                    config=s3_config
                )
            
            # Test connection by checking if bucket exists
            if self.bucket_name:
                try:
                    self.s3_client.head_bucket(Bucket=self.bucket_name)
                    logger.info("S3 storage initialized successfully", bucket=self.bucket_name)
                except ClientError as e:
                    error_code = e.response['Error']['Code']
                    if error_code == '404':
                        # Bucket doesn't exist, create it
                        try:
                            self.s3_client.create_bucket(Bucket=self.bucket_name)
                            logger.info("S3 bucket created", bucket=self.bucket_name)
                        except Exception as create_error:
                            logger.error("Failed to create S3 bucket", bucket=self.bucket_name, error=str(create_error))
                    else:
                        logger.error("Failed to access S3 bucket", bucket=self.bucket_name, error=str(e))
        except Exception as e:
            logger.error("Failed to initialize S3 client", error=str(e))
            self.s3_client = None
    
    def is_available(self) -> bool:
        """Check if storage is available"""
        return self.s3_client is not None and self.bucket_name is not None
    
    def upload_file(
        self,
        file_content: bytes,
        file_name: str,
        content_type: str = "application/octet-stream",
        folder: str = "uploads"
    ) -> Optional[dict]:
        """
        Upload file to S3/MinIO
        
        Returns:
            dict with 'url', 'key', 'size' or None if failed
        """
        if not self.is_available():
            logger.warning("Storage not available, file upload skipped")
            return None
        
        try:
            # Generate unique file key
            file_ext = os.path.splitext(file_name)[1]
            file_key = f"{folder}/{uuid.uuid4()}{file_ext}"
            
            # Upload file
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=file_content,
                ContentType=content_type,
                Metadata={
                    'original_name': file_name,
                    'uploaded_at': datetime.utcnow().isoformat()
                }
            )
            
            # Generate URL (presigned URL for private buckets, or public URL)
            if settings.USE_MINIO:
                url = f"{settings.S3_ENDPOINT_URL}/{self.bucket_name}/{file_key}"
            else:
                url = self.s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': self.bucket_name, 'Key': file_key},
                    ExpiresIn=3600 * 24 * 7  # 7 days
                )
            
            result = {
                'url': url,
                'key': file_key,
                'size': len(file_content),
                'content_type': content_type,
                'original_name': file_name
            }
            
            logger.info("File uploaded successfully", file_key=file_key, size=len(file_content))
            return result
        
        except Exception as e:
            logger.error("Failed to upload file", file_name=file_name, error=str(e), exc_info=True)
            return None
    
    def delete_file(self, file_key: str) -> bool:
        """Delete file from S3/MinIO"""
        if not self.is_available():
            return False
        
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_key)
            logger.info("File deleted successfully", file_key=file_key)
            return True
        except Exception as e:
            logger.error("Failed to delete file", file_key=file_key, error=str(e))
            return False
    
    def get_file_url(self, file_key: str, expires_in: int = 3600) -> Optional[str]:
        """Get presigned URL for file"""
        if not self.is_available():
            return None
        
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': file_key},
                ExpiresIn=expires_in
            )
            return url
        except Exception as e:
            logger.error("Failed to generate file URL", file_key=file_key, error=str(e))
            return None
    
    def get_file(self, file_key: str) -> Optional[bytes]:
        """Download file from S3/MinIO"""
        if not self.is_available():
            return None
        
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=file_key)
            return response['Body'].read()
        except Exception as e:
            logger.error("Failed to download file", file_key=file_key, error=str(e))
            return None


# Global storage service instance
storage_service = StorageService()

