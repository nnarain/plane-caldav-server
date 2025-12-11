"""
Tests for custom CalDAV application
"""
import pytest
import tempfile
import shutil
from unittest.mock import Mock, MagicMock, patch
from radicale import config

from plane_caldav_server.caldav_app import PlaneCalDAVApplication
from plane_caldav_server.sync_manager import SyncManager


class TestPlaneCalDAVApplication:
    """Test suite for custom CalDAV application."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp)
    
    @pytest.fixture
    def mock_config(self, temp_dir):
        """Create a proper configuration."""
        # Use radicale's config loader to get a valid configuration
        configuration = config.load()
        # Override storage folder to use temp directory
        configuration.update({
            "storage": {"filesystem_folder": temp_dir}
        }, "test config")
        return configuration
    
    @pytest.fixture
    def mock_sync_manager(self):
        """Create a mock sync manager."""
        manager = MagicMock(spec=SyncManager)
        return manager
    
    def test_init_without_sync_manager(self, mock_config):
        """Test initialization without sync manager."""
        app = PlaneCalDAVApplication(mock_config)
        assert app.sync_manager is None
    
    def test_init_with_sync_manager(self, mock_config, mock_sync_manager):
        """Test initialization with sync manager."""
        app = PlaneCalDAVApplication(mock_config, mock_sync_manager)
        assert app.sync_manager is mock_sync_manager
    
    @patch('plane_caldav_server.caldav_app.Application.do_GET')
    def test_do_get_calls_sync(self, mock_parent_get, mock_config, mock_sync_manager):
        """Test that do_GET calls sync before handling request."""
        app = PlaneCalDAVApplication(mock_config, mock_sync_manager)
        
        # Mock the parent's do_GET return value
        mock_parent_get.return_value = (200, {}, [b"OK"])
        
        # Call do_GET
        environ = {}
        base_prefix = ""
        path = "/testuser/plane-tasks/"
        user = "testuser"
        
        result = app.do_GET(environ, base_prefix, path, user)
        
        # Verify sync was called
        mock_sync_manager.sync.assert_called_once()
        
        # Verify parent method was called
        mock_parent_get.assert_called_once_with(environ, base_prefix, path, user)
        
        # Verify result
        assert result == (200, {}, [b"OK"])
    
    @patch('plane_caldav_server.caldav_app.Application.do_POST')
    def test_do_post_calls_sync(self, mock_parent_post, mock_config, mock_sync_manager):
        """Test that do_POST calls sync before handling request."""
        app = PlaneCalDAVApplication(mock_config, mock_sync_manager)
        
        # Mock the parent's do_POST return value
        mock_parent_post.return_value = (201, {}, [b"Created"])
        
        # Call do_POST
        environ = {}
        base_prefix = ""
        path = "/testuser/plane-tasks/"
        user = "testuser"
        
        result = app.do_POST(environ, base_prefix, path, user)
        
        # Verify sync was called
        mock_sync_manager.sync.assert_called_once()
        
        # Verify parent method was called
        mock_parent_post.assert_called_once_with(environ, base_prefix, path, user)
        
        # Verify result
        assert result == (201, {}, [b"Created"])
    
    @patch('plane_caldav_server.caldav_app.Application.do_GET')
    def test_do_get_without_sync_manager(self, mock_parent_get, mock_config):
        """Test that do_GET works without sync manager."""
        app = PlaneCalDAVApplication(mock_config, None)
        
        # Mock the parent's do_GET return value
        mock_parent_get.return_value = (200, {}, [b"OK"])
        
        # Call do_GET
        environ = {}
        base_prefix = ""
        path = "/testuser/plane-tasks/"
        user = "testuser"
        
        result = app.do_GET(environ, base_prefix, path, user)
        
        # Verify parent method was called
        mock_parent_get.assert_called_once_with(environ, base_prefix, path, user)
        
        # Verify result
        assert result == (200, {}, [b"OK"])
    
    @patch('plane_caldav_server.caldav_app.Application.do_POST')
    def test_do_post_without_sync_manager(self, mock_parent_post, mock_config):
        """Test that do_POST works without sync manager."""
        app = PlaneCalDAVApplication(mock_config, None)
        
        # Mock the parent's do_POST return value
        mock_parent_post.return_value = (201, {}, [b"Created"])
        
        # Call do_POST
        environ = {}
        base_prefix = ""
        path = "/testuser/plane-tasks/"
        user = "testuser"
        
        result = app.do_POST(environ, base_prefix, path, user)
        
        # Verify parent method was called
        mock_parent_post.assert_called_once_with(environ, base_prefix, path, user)
        
        # Verify result
        assert result == (201, {}, [b"Created"])
