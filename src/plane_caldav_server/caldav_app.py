"""
Custom CalDAV application that syncs with Plane on requests.
"""
from typing import Any, Callable, Iterable, List, Mapping, Optional, Tuple
from radicale import Application

from plane_caldav_server.sync_manager import SyncManager


class PlaneCalDAVApplication(Application):
    """Custom CalDAV application that syncs with Plane on GET and POST requests."""
    
    def __init__(self, configuration, sync_manager: Optional[SyncManager] = None):
        """
        Initialize the custom application.
        
        Args:
            configuration: Radicale configuration
            sync_manager: Optional sync manager for Plane integration
        """
        super().__init__(configuration)
        self.sync_manager = sync_manager
        
    def do_GET(
        self,
        environ: Mapping[str, Any],
        base_prefix: str,
        path: str,
        user: str
    ) -> Tuple[int, Mapping[str, str], Iterable[bytes]]:
        """
        Handle GET requests with sync before fetching data.
        
        Args:
            environ: WSGI environment
            base_prefix: Base URL prefix
            path: Request path
            user: Authenticated user
            
        Returns:
            Tuple of (status_code, headers, body)
        """
        # Sync before handling GET request
        if self.sync_manager:
            self.sync_manager.sync()
            
        # Call parent implementation
        return super().do_GET(environ, base_prefix, path, user)
        
    def do_POST(
        self,
        environ: Mapping[str, Any],
        base_prefix: str,
        path: str,
        user: str
    ) -> Tuple[int, Mapping[str, str], Iterable[bytes]]:
        """
        Handle POST requests with sync before updating data.
        
        Args:
            environ: WSGI environment
            base_prefix: Base URL prefix
            path: Request path
            user: Authenticated user
            
        Returns:
            Tuple of (status_code, headers, body)
        """
        # Sync before handling POST request
        if self.sync_manager:
            self.sync_manager.sync()
            
        # Call parent implementation
        return super().do_POST(environ, base_prefix, path, user)
