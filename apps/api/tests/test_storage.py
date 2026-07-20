import os
import io
import pytest
from apps.api.core.storage import get_storage_provider, StorageError, LocalStorageProvider, S3StorageProvider

def test_local_storage_lifecycle(tmp_path):
    # Using pytest's tmp_path to isolate filesystem tests
    provider = get_storage_provider("local", base_directory=str(tmp_path))
    
    filename = "test_dataset.csv"
    content = b"header1,header2\n1,2"
    
    # Generate path
    rel_path, abs_path = provider.generate_path(filename)
    assert rel_path.endswith(".csv")
    
    # Doesn't exist initially
    assert not provider.exists(rel_path)
    
    # Save file
    file_stream = io.BytesIO(content)
    saved_path = provider.save(file_stream, rel_path)
    assert saved_path == rel_path
    
    # Check it exists
    assert provider.exists(rel_path)
    
    # Check metadata
    meta = provider.metadata(rel_path)
    assert meta["size_bytes"] == len(content)
    assert meta["extension"] == ".csv"
    
    # Get file
    retrieved_stream = provider.get(rel_path)
    retrieved_content = retrieved_stream.read()
    assert retrieved_content == content
    retrieved_stream.close()
    
    # Delete file
    deleted = provider.delete(rel_path)
    assert deleted is True
    assert not provider.exists(rel_path)


def test_local_storage_file_not_found(tmp_path):
    provider = get_storage_provider("local", base_directory=str(tmp_path))
    
    with pytest.raises(StorageError) as exc_info:
        provider.get("non_existent.csv")
    assert "File not found" in str(exc_info.value)
    
    with pytest.raises(StorageError) as exc_info:
        provider.metadata("non_existent.csv")
    assert "File not found" in str(exc_info.value)
    
    # Deleting non-existent file returns False instead of raising an error
    assert provider.delete("non_existent.csv") is False


def test_s3_storage_unconfigured():
    provider = get_storage_provider("s3", bucket_name="", access_key="", secret_key="")
    
    # Generating path should work regardless of configuration since it's just string manipulation
    rel_path, abs_path = provider.generate_path("test.csv")
    assert rel_path.startswith("datasets/")
    
    # Operations should raise NotImplementedError
    file_stream = io.BytesIO(b"content")
    with pytest.raises(NotImplementedError):
        provider.save(file_stream, rel_path)
        
    with pytest.raises(NotImplementedError):
        provider.get(rel_path)


def test_factory():
    local_provider = get_storage_provider("local")
    assert isinstance(local_provider, LocalStorageProvider)
    
    s3_provider = get_storage_provider("s3", bucket_name="test")
    assert isinstance(s3_provider, S3StorageProvider)
