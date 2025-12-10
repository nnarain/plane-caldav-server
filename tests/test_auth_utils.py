"""
Tests for authentication utilities
"""
import os
import tempfile
import pytest
from pathlib import Path
from passlib.hash import apr_md5_crypt

from plane_caldav_server.auth_utils import (
    generate_htpasswd_file,
    get_credentials_from_env
)


class TestGenerateHtpasswdFile:
    """Tests for generate_htpasswd_file function"""

    def test_generate_htpasswd_file_creates_file(self):
        """Test that htpasswd file is created with correct content"""
        with tempfile.TemporaryDirectory() as tmpdir:
            htpasswd_path = Path(tmpdir) / "test_htpasswd"
            username = "testuser"
            password = "testpassword"

            generate_htpasswd_file(str(htpasswd_path), username, password)

            # Verify file exists
            assert htpasswd_path.exists()

            # Read file and verify format
            content = htpasswd_path.read_text()
            assert content.startswith(f"{username}:$apr1$")
            
            # Extract hash and verify password
            _, password_hash = content.strip().split(":", 1)
            assert apr_md5_crypt.verify(password, password_hash)

    def test_generate_htpasswd_file_overwrites_existing(self):
        """Test that existing htpasswd file is overwritten"""
        with tempfile.TemporaryDirectory() as tmpdir:
            htpasswd_path = Path(tmpdir) / "test_htpasswd"
            
            # Create initial file
            generate_htpasswd_file(str(htpasswd_path), "user1", "pass1")
            
            # Overwrite with new credentials
            generate_htpasswd_file(str(htpasswd_path), "user2", "pass2")

            # Verify only new credentials are in file
            content = htpasswd_path.read_text()
            assert "user2:" in content
            assert "user1:" not in content


class TestGetCredentialsFromEnv:
    """Tests for get_credentials_from_env function"""

    def test_get_credentials_from_env_success(self):
        """Test successful retrieval of credentials from environment"""
        os.environ["USER"] = "envuser"
        os.environ["PASSWORD"] = "envpass"
        
        try:
            username, password = get_credentials_from_env()
            assert username == "envuser"
            assert password == "envpass"
        finally:
            # Clean up
            os.environ.pop("USER", None)
            os.environ.pop("PASSWORD", None)

    def test_get_credentials_from_env_missing_user(self):
        """Test that ValueError is raised when USER is missing"""
        # Ensure USER is not set
        os.environ.pop("USER", None)
        os.environ["PASSWORD"] = "envpass"
        
        try:
            with pytest.raises(ValueError, match="USER environment variable is required"):
                get_credentials_from_env()
        finally:
            os.environ.pop("PASSWORD", None)

    def test_get_credentials_from_env_missing_password(self):
        """Test that ValueError is raised when PASSWORD is missing"""
        os.environ["USER"] = "envuser"
        os.environ.pop("PASSWORD", None)
        
        try:
            with pytest.raises(ValueError, match="PASSWORD environment variable is required"):
                get_credentials_from_env()
        finally:
            os.environ.pop("USER", None)

    def test_get_credentials_from_env_missing_both(self):
        """Test that ValueError is raised when both are missing"""
        os.environ.pop("USER", None)
        os.environ.pop("PASSWORD", None)
        
        with pytest.raises(ValueError, match="USER environment variable is required"):
            get_credentials_from_env()
