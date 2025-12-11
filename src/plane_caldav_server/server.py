"""
CalDAV server application that integrates with Plane Project Management.
"""
import os
from radicale import config
from wsgiref.simple_server import make_server
from argparse import ArgumentParser

from plane_caldav_server.plane import PlaneAPI
from plane_caldav_server.calendar_utils import (
    create_calendar_collection,
    add_todo_to_calendar,
    list_todos
)
from plane_caldav_server.auth_utils import generate_htpasswd_file
from plane_caldav_server.sync_manager import SyncManager
from plane_caldav_server.caldav_app import PlaneCalDAVApplication


def run_server(args, sync_manager=None):
    """Start the CalDAV server with the given configuration."""
    # Use the load function to create a proper configuration
    configuration = config.load()

    # Override storage folder and authentication
    configuration.update({
        "storage": {"filesystem_folder": args.storage_folder},
        "auth": {
            "type": "htpasswd",
            "htpasswd_filename": args.htpasswd_file,
            "htpasswd_encryption": "md5"
        }
    }, "custom config")

    app = PlaneCalDAVApplication(configuration, sync_manager)

    with make_server(args.host, args.port, app) as httpd:
        print(f"Serving on {args.host}:{args.port}...")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        print("Server stopped.")


def sync_plane_tasks(args):
    """Sync tasks from Plane to CalDAV."""
    # Initialize Plane API client
    plane_api = PlaneAPI(args.plane_url, args.api_key)

    # Get a list of work items from plane
    tasks = []

    projects = plane_api.get_projects(args.workspace)
    for project in projects:
        print(f"Project: {project['name']}")
        work_items = plane_api.get_work_items(args.workspace, project["id"])
        for item in work_items:
            print(f"  Work Item: {item['name']}")
            tasks.append(item)

    # Create calendar collection for the user
    calendar_path = create_calendar_collection(args.storage_folder, args.user, "plane-tasks")
    print(f"Calendar created at: {calendar_path}")
    print(f"Access via CalDAV at: http://{args.host}:{args.port}/{args.user}/plane-tasks/")

    # Add tasks as todos to the calendar
    for task in tasks:
        add_todo_to_calendar(
            calendar_path,
            summary=task['name'],
            description=task.get('description', ''),
            status='COMPLETED' if task.get('completed_at') else 'NEEDS-ACTION'
        )
        print(f"Added TODO for work item: {task['name']}")


def main():
    """Main entry point for the server."""
    parser = ArgumentParser(description="Plane CalDAV Server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to run the server on")
    parser.add_argument("--port", type=int, default=5232, help="Port to run the server on")
    parser.add_argument("--storage-folder", type=str, default="./collections", help="Folder to store calendar collections")
    parser.add_argument("--user", type=str, default="testuser", help="Username for X-Remote-User authentication")
    parser.add_argument("--password", type=str, help="Password for authentication")
    parser.add_argument("--htpasswd-file", type=str, default="./htpasswd", help="Path to htpasswd file")

    parser.add_argument("--plane-url", type=str, help="Base URL for Plane Project Management API")
    parser.add_argument("--api-key", type=str, help="API key for Plane Project Management API")
    parser.add_argument("--workspace", type=str, default="default", help="Workspace slug in Plane")
    parser.add_argument("--sync-only", action="store_true", help="Only sync tasks from Plane, don't start server")

    args = parser.parse_args()

    # Generate htpasswd file from environment variables or command line args
    username = os.environ.get("USER", args.user)
    password = os.environ.get("PASSWORD", args.password)
    
    if password:
        print(f"Generating htpasswd file for user: {username}")
        generate_htpasswd_file(args.htpasswd_file, username, password)
    else:
        print(f"No password provided, using existing htpasswd file: {args.htpasswd_file}")
    
    # Update args.user to use the environment variable if set
    args.user = username

    # Create sync manager if Plane is configured
    sync_manager = None
    if args.plane_url and args.api_key:
        sync_manager = SyncManager(
            plane_url=args.plane_url,
            api_key=args.api_key,
            workspace=args.workspace,
            storage_folder=args.storage_folder,
            user=args.user,
            calendar_name="plane-tasks"
        )
        
        # Perform initial sync
        print("Performing initial sync from Plane...")
        sync_manager.sync(force=True)
        print("Initial sync completed")
        
        if args.sync_only:
            print("Sync-only mode, exiting...")
            return

    # Start the CalDAV server
    run_server(args, sync_manager)


if __name__ == "__main__":
    main()
