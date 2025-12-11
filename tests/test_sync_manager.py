"""
Tests for sync manager
"""
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import time

from plane_caldav_server.sync_manager import SyncManager


class TestSyncManager:
    """Test suite for sync manager."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp)
    
    @pytest.fixture
    def sync_manager(self, temp_dir):
        """Create a sync manager instance."""
        return SyncManager(
            plane_url="https://test.plane.so",
            api_key="test-api-key",
            workspace="test-workspace",
            storage_folder=temp_dir,
            user="testuser",
            calendar_name="test-calendar"
        )
    
    def test_init(self, temp_dir):
        """Test sync manager initialization."""
        manager = SyncManager(
            plane_url="https://test.plane.so",
            api_key="test-api-key",
            workspace="test-workspace",
            storage_folder=temp_dir,
            user="testuser",
            calendar_name="test-calendar"
        )
        
        assert manager.plane_url == "https://test.plane.so"
        assert manager.api_key == "test-api-key"
        assert manager.workspace == "test-workspace"
        assert manager.storage_folder == temp_dir
        assert manager.user == "testuser"
        assert manager.calendar_name == "test-calendar"
    
    @patch('plane_caldav_server.sync_manager.PlaneAPI')
    def test_sync_creates_todos(self, mock_plane_api_class, sync_manager):
        """Test that sync creates todos from Plane tasks."""
        # Mock the PlaneAPI
        mock_plane_api = MagicMock()
        mock_plane_api_class.return_value = mock_plane_api
        
        # Mock projects
        mock_plane_api.get_projects.return_value = [
            {"id": "project1", "name": "Project 1"}
        ]
        
        # Mock work items
        mock_plane_api.get_work_items.return_value = [
            {
                "id": "task1",
                "name": "Task 1",
                "description": "Description 1",
                "completed_at": None
            },
            {
                "id": "task2",
                "name": "Task 2",
                "description": "Description 2",
                "completed_at": "2024-01-01"
            }
        ]
        
        # Perform sync
        result = sync_manager.sync(force=True)
        
        assert result is True
        
        # Verify PlaneAPI was called correctly
        mock_plane_api.get_projects.assert_called_once_with("test-workspace")
        mock_plane_api.get_work_items.assert_called_once_with("test-workspace", "project1")
        
        # Verify calendar was created and todos were added
        calendar_path = Path(sync_manager.storage_folder) / "collection-root" / "testuser" / "test-calendar"
        assert calendar_path.exists()
        
        # Check that todo files were created
        ics_files = list(calendar_path.glob("*.ics"))
        assert len(ics_files) == 2
    
    @patch('plane_caldav_server.sync_manager.PlaneAPI')
    def test_sync_respects_interval(self, mock_plane_api_class, sync_manager):
        """Test that sync respects the minimum interval."""
        # Mock the PlaneAPI
        mock_plane_api = MagicMock()
        mock_plane_api_class.return_value = mock_plane_api
        mock_plane_api.get_projects.return_value = []
        
        # First sync should succeed
        result1 = sync_manager.sync(force=True)
        assert result1 is True
        
        # Immediate second sync should be skipped
        result2 = sync_manager.sync()
        assert result2 is False
        
        # Force sync should work
        result3 = sync_manager.sync(force=True)
        assert result3 is True
    
    @patch('plane_caldav_server.sync_manager.PlaneAPI')
    def test_sync_avoids_duplicates(self, mock_plane_api_class, sync_manager):
        """Test that sync avoids creating duplicate todos."""
        # Mock the PlaneAPI
        mock_plane_api = MagicMock()
        mock_plane_api_class.return_value = mock_plane_api
        
        # Mock projects
        mock_plane_api.get_projects.return_value = [
            {"id": "project1", "name": "Project 1"}
        ]
        
        # Mock work items (same task returned both times)
        mock_plane_api.get_work_items.return_value = [
            {
                "id": "task1",
                "name": "Task 1",
                "description": "Description 1",
                "completed_at": None
            }
        ]
        
        # First sync
        sync_manager.sync(force=True)
        
        # Second sync (forced)
        sync_manager.sync(force=True)
        
        # Verify only one todo file was created
        calendar_path = Path(sync_manager.storage_folder) / "collection-root" / "testuser" / "test-calendar"
        ics_files = list(calendar_path.glob("*.ics"))
        assert len(ics_files) == 1
    
    @patch('plane_caldav_server.sync_manager.PlaneAPI')
    def test_sync_handles_errors(self, mock_plane_api_class, sync_manager):
        """Test that sync handles errors gracefully."""
        # Mock the PlaneAPI to raise an exception
        mock_plane_api = MagicMock()
        mock_plane_api_class.return_value = mock_plane_api
        mock_plane_api.get_projects.side_effect = Exception("API Error")
        
        # Sync should return False on error
        result = sync_manager.sync(force=True)
        assert result is False
