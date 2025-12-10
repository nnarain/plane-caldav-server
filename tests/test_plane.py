"""
Tests for Plane API client
"""
import pytest
from unittest.mock import Mock, patch
from plane_caldav_server.plane import PlaneAPI


class TestPlaneAPI:
    """Test suite for Plane API client."""
    
    @pytest.fixture
    def api_client(self):
        """Create a Plane API client for testing."""
        return PlaneAPI("http://test.example.com", "test_api_key")
    
    def test_init(self, api_client):
        """Test API client initialization."""
        assert api_client.api_key == "test_api_key"
        assert api_client._base_api_url == "http://test.example.com/api/v1"
    
    @patch('plane_caldav_server.plane.requests.get')
    def test_get_projects(self, mock_get, api_client):
        """Test getting projects from Plane."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {"id": "1", "name": "Project 1"},
                {"id": "2", "name": "Project 2"},
            ]
        }
        mock_get.return_value = mock_response
        
        projects = api_client.get_projects("test-workspace")
        
        assert len(projects) == 2
        assert projects[0]["id"] == "1"
        assert projects[0]["name"] == "Project 1"
    
    @patch('plane_caldav_server.plane.requests.get')
    def test_get_work_items(self, mock_get, api_client):
        """Test getting work items from Plane."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {
                    "id": "1",
                    "name": "Task 1",
                    "description_stripped": "Description 1",
                    "target_date": "2025-12-31",
                    "completed_at": None
                }
            ]
        }
        mock_get.return_value = mock_response
        
        work_items = api_client.get_work_items("test-workspace", "project-1")
        
        assert len(work_items) == 1
        assert work_items[0]["name"] == "Task 1"
        assert work_items[0]["completed_at"] is None
