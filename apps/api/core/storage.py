import os
import uuid
import shutil
from abc import ABC, abstractmethod
from typing import BinaryIO, Dict, Any, Tuple
from pathlib import Path

class StorageError(Exception):
    """Base exception for storage related operations."""
    pass


class StorageProvider(ABC):
    """Abstract interface for dataset storage."""
    
    @abstractmethod
    def save(self, file_obj: BinaryIO, destination: str) -> str:
        """Saves a file stream to the destination and returns the path/key."""
        pass
        
    @abstractmethod
    def get(self, path: str) -> BinaryIO:
        """Retrieves a file stream from the specified path/key."""
        pass
        
    @abstractmethod
    def delete(self, path: str) -> bool:
        """Deletes the file at the specified path/key."""
        pass
        
    @abstractmethod
    def exists(self, path: str) -> bool:
        """Checks if a file exists at the specified path/key."""
        pass
        
    @abstractmethod
    def generate_path(self, original_filename: str) -> Tuple[str, str]:
        """
        Generates a unique path/key for a file.
        Returns (relative_path_or_key, full_absolute_path_if_applicable).
        """
        pass
        
    @abstractmethod
    def metadata(self, path: str) -> Dict[str, Any]:
        """Retrieves metadata (size, etc) for the file."""
        pass


class LocalStorageProvider(StorageProvider):
    """Local file system implementation for development environments."""
    
    def __init__(self, base_directory: str = "data/datasets"):
        self.base_dir = Path(base_directory)
        
        # Ensure base directory exists, but don't fail if permissions issue during init
        # We will handle permission errors during actual operations
        try:
            self.base_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise StorageError(f"Failed to initialize local storage at {self.base_dir}: {e}")

    def generate_path(self, original_filename: str) -> Tuple[str, str]:
        # Generate a unique ID (e.g. for dataset_version_id)
        unique_id = str(uuid.uuid4())
        ext = os.path.splitext(original_filename)[1]
        relative_path = f"{unique_id}{ext}"
        
        # Absolute path where it will be saved
        full_path = str(self.base_dir / relative_path)
        return relative_path, full_path

    def save(self, file_obj: BinaryIO, destination: str) -> str:
        target_path = self.base_dir / destination
        try:
            # Ensure parent directories exist (in case destination contains folders)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            with open(target_path, "wb") as f:
                shutil.copyfileobj(file_obj, f)
            return destination
        except PermissionError:
            raise StorageError(f"Permission denied: Unable to write to {target_path}")
        except Exception as e:
            raise StorageError(f"Failed to save file to local storage: {e}")

    def get(self, path: str) -> BinaryIO:
        target_path = self.base_dir / path
        if not target_path.exists():
            raise StorageError(f"File not found: {path}")
            
        try:
            return open(target_path, "rb")
        except PermissionError:
            raise StorageError(f"Permission denied: Unable to read from {target_path}")
        except Exception as e:
            raise StorageError(f"Failed to retrieve file from local storage: {e}")

    def delete(self, path: str) -> bool:
        target_path = self.base_dir / path
        if not target_path.exists():
            return False
            
        try:
            target_path.unlink()
            return True
        except PermissionError:
            raise StorageError(f"Permission denied: Unable to delete {target_path}")
        except Exception as e:
            raise StorageError(f"Failed to delete file from local storage: {e}")

    def exists(self, path: str) -> bool:
        return (self.base_dir / path).exists()

    def metadata(self, path: str) -> Dict[str, Any]:
        target_path = self.base_dir / path
        if not target_path.exists():
            raise StorageError(f"File not found: {path}")
            
        try:
            stat_info = target_path.stat()
            return {
                "size_bytes": stat_info.st_size,
                "created_at": stat_info.st_ctime,
                "modified_at": stat_info.st_mtime,
                "extension": target_path.suffix,
            }
        except Exception as e:
            raise StorageError(f"Failed to retrieve metadata: {e}")


class S3StorageProvider(StorageProvider):
    """S3/MinIO implementation for production/cloud environments."""
    
    def __init__(self, bucket_name: str, endpoint_url: str = None, access_key: str = None, secret_key: str = None):
        self.bucket_name = bucket_name
        self.endpoint_url = endpoint_url
        self.access_key = access_key
        self.secret_key = secret_key
        
        # We perform a lazy check here to allow instantiation for dependency injection testing
        if not all([bucket_name, access_key, secret_key]):
            self._configured = False
        else:
            self._configured = True
            
    def _check_config(self):
        if not self._configured:
            raise NotImplementedError("S3 storage credentials are not fully configured.")

    def generate_path(self, original_filename: str) -> Tuple[str, str]:
        unique_id = str(uuid.uuid4())
        ext = os.path.splitext(original_filename)[1]
        s3_key = f"datasets/{unique_id}{ext}"
        return s3_key, f"s3://{self.bucket_name}/{s3_key}"

    def save(self, file_obj: BinaryIO, destination: str) -> str:
        self._check_config()
        raise NotImplementedError("S3 save is not implemented yet.")

    def get(self, path: str) -> BinaryIO:
        self._check_config()
        raise NotImplementedError("S3 get is not implemented yet.")

    def delete(self, path: str) -> bool:
        self._check_config()
        raise NotImplementedError("S3 delete is not implemented yet.")

    def exists(self, path: str) -> bool:
        self._check_config()
        raise NotImplementedError("S3 exists is not implemented yet.")

    def metadata(self, path: str) -> Dict[str, Any]:
        self._check_config()
        raise NotImplementedError("S3 metadata is not implemented yet.")


def get_storage_provider(provider_type: str = "local", **kwargs) -> StorageProvider:
    """Factory function for retrieving the configured storage provider."""
    if provider_type.lower() == "s3":
        return S3StorageProvider(**kwargs)
    return LocalStorageProvider(**kwargs)
