"""
Tests for calendar utilities
"""
import pytest
from pathlib import Path
from datetime import datetime, timedelta
import tempfile
import shutil

from plane_caldav_server.calendar_utils import (
    create_calendar_collection,
    create_todo,
    add_todo_to_calendar,
    list_todos,
)


class TestCalendarUtils:
    """Test suite for calendar utility functions."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp)
    
    def test_create_calendar_collection(self, temp_dir):
        """Test creating a calendar collection."""
        calendar_path = create_calendar_collection(temp_dir, "testuser", "testcalendar")
        
        assert calendar_path.exists()
        assert calendar_path.is_dir()
        assert (calendar_path / ".Radicale.props").exists()
    
    def test_create_todo(self):
        """Test creating a TODO component."""
        cal = create_todo(
            summary="Test TODO",
            description="This is a test",
            priority=1,
            status="NEEDS-ACTION"
        )
        
        assert cal is not None
        # Verify it has a VTODO component
        has_todo = False
        for component in cal.walk():
            if component.name == "VTODO":
                has_todo = True
                assert str(component.get('summary')) == "Test TODO"
                break
        assert has_todo
    
    def test_add_todo_to_calendar(self, temp_dir):
        """Test adding a TODO to a calendar."""
        calendar_path = create_calendar_collection(temp_dir, "testuser", "testcalendar")
        
        file_path = add_todo_to_calendar(
            calendar_path,
            summary="Test Task",
            description="Test Description",
            priority=2
        )
        
        assert file_path.exists()
        assert file_path.suffix == ".ics"
    
    def test_list_todos(self, temp_dir):
        """Test listing TODOs in a calendar."""
        calendar_path = create_calendar_collection(temp_dir, "testuser", "testcalendar")
        
        # Add some TODOs
        add_todo_to_calendar(calendar_path, summary="Task 1")
        add_todo_to_calendar(calendar_path, summary="Task 2")
        add_todo_to_calendar(calendar_path, summary="Task 3")
        
        todos = list_todos(calendar_path)
        
        assert len(todos) == 3
        summaries = [todo['summary'] for todo in todos]
        assert "Task 1" in summaries
        assert "Task 2" in summaries
        assert "Task 3" in summaries
