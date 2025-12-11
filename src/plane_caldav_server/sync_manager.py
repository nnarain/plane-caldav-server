"""
Sync manager for synchronizing Plane tasks with CalDAV calendar.
"""
from pathlib import Path
from typing import Optional
import threading
import time

from plane_caldav_server.plane import PlaneAPI
from plane_caldav_server.calendar_utils import (
    create_calendar_collection,
    add_todo_to_calendar,
    list_todos
)


class SyncManager:
    """Manages synchronization between Plane and CalDAV calendar."""
    
    def __init__(
        self,
        plane_url: str,
        api_key: str,
        workspace: str,
        storage_folder: str,
        user: str,
        calendar_name: str = "plane-tasks"
    ):
        """
        Initialize the sync manager.
        
        Args:
            plane_url: Base URL for Plane Project Management API
            api_key: API key for Plane Project Management API
            workspace: Workspace slug in Plane
            storage_folder: Folder to store calendar collections
            user: Username for CalDAV
            calendar_name: Name of the calendar to sync to
        """
        self.plane_url = plane_url
        self.api_key = api_key
        self.workspace = workspace
        self.storage_folder = storage_folder
        self.user = user
        self.calendar_name = calendar_name
        self._lock = threading.Lock()
        self._last_sync_time = 0
        self._sync_interval = 60  # Minimum seconds between syncs
        
    def sync(self, force: bool = False) -> bool:
        """
        Sync tasks from Plane to CalDAV calendar.
        
        Args:
            force: Force sync even if within sync interval
            
        Returns:
            True if sync was performed, False if skipped
        """
        # Check if we should sync based on time interval
        current_time = time.time()
        if not force and (current_time - self._last_sync_time) < self._sync_interval:
            return False
            
        with self._lock:
            # Double-check after acquiring lock
            current_time = time.time()
            if not force and (current_time - self._last_sync_time) < self._sync_interval:
                return False
                
            try:
                self._perform_sync()
                self._last_sync_time = current_time
                return True
            except Exception as e:
                print(f"Error during sync: {e}")
                return False
                
    def _perform_sync(self):
        """Perform the actual sync operation."""
        # Initialize Plane API client
        plane_api = PlaneAPI(self.plane_url, self.api_key)
        
        # Get a list of work items from plane
        tasks = []
        
        projects = plane_api.get_projects(self.workspace)
        for project in projects:
            work_items = plane_api.get_work_items(self.workspace, project["id"])
            tasks.extend(work_items)
        
        # Create calendar collection for the user
        calendar_path = create_calendar_collection(
            self.storage_folder,
            self.user,
            self.calendar_name
        )
        
        # Get existing todos to avoid duplicates
        existing_todos = list_todos(calendar_path)
        existing_uids = {todo['uid'] for todo in existing_todos}
        
        # Add new tasks as todos to the calendar
        for task in tasks:
            # Use task ID as UID to avoid duplicates
            task_uid = f"plane-task-{task['id']}"
            
            # Skip if this task already exists
            if task_uid in existing_uids:
                continue
                
            add_todo_to_calendar(
                calendar_path,
                summary=task['name'],
                description=task.get('description', ''),
                status='COMPLETED' if task.get('completed_at') else 'NEEDS-ACTION',
                uid=task_uid
            )
