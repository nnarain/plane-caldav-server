"""
Example script showing how to create calendar collections and add TODOs on the server side.
"""
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from plane_caldav_server.calendar_utils import (
    create_calendar_collection,
    add_todo_to_calendar,
    list_todos
)
from datetime import datetime, timedelta


def main():
    # Configuration
    base_path = "./collections"
    user = "testuser"
    calendar_name = "tasks"
    
    # 1. Create a calendar collection
    print(f"Creating calendar collection: {user}/{calendar_name}")
    calendar_path = create_calendar_collection(base_path, user, calendar_name)
    print(f"Calendar created at: {calendar_path}")
    
    # 2. Add some example TODOs
    print("\nAdding TODOs...")
    
    # Simple TODO
    todo1 = add_todo_to_calendar(
        calendar_path,
        summary="Complete project documentation",
        description="Write comprehensive docs for the CalDAV server project",
        priority=1,
        status="NEEDS-ACTION"
    )
    print(f"Created TODO: {todo1.name}")
    
    # TODO with due date
    todo2 = add_todo_to_calendar(
        calendar_path,
        summary="Review pull requests",
        description="Check and review pending PRs",
        priority=2,
        status="IN-PROCESS",
        due=datetime.now() + timedelta(days=2)
    )
    print(f"Created TODO: {todo2.name}")
    
    # High priority TODO
    todo3 = add_todo_to_calendar(
        calendar_path,
        summary="Fix critical bug in authentication",
        description="Users are unable to log in",
        priority=1,
        status="NEEDS-ACTION",
        due=datetime.now() + timedelta(hours=4)
    )
    print(f"Created TODO: {todo3.name}")
    
    # Completed TODO
    todo4 = add_todo_to_calendar(
        calendar_path,
        summary="Set up development environment",
        description="Install dependencies and configure tools",
        priority=3,
        status="COMPLETED"
    )
    print(f"Created TODO: {todo4.name}")
    
    # 3. List all TODOs
    print("\nListing all TODOs in calendar:")
    todos = list_todos(calendar_path)
    for todo in todos:
        print(f"  - [{todo['status']}] {todo['summary']} (Priority: {todo['priority']})")
    
    print(f"\nTotal TODOs: {len(todos)}")
    print("\nYou can now access these TODOs via CalDAV at:")
    print(f"http://localhost:5232/{user}/{calendar_name}/")


if __name__ == "__main__":
    main()
