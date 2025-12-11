"""
Utility functions for creating and managing calendar files on the server side.
"""
import os
from pathlib import Path
from datetime import datetime
from icalendar import Calendar, Todo
import uuid


def create_calendar_collection(base_path: str, user: str, calendar_name: str) -> Path:
    """
    Create a calendar collection directory structure for a user.
    
    Args:
        base_path: Base collections directory path
        user: Username
        calendar_name: Name of the calendar
        
    Returns:
        Path to the created calendar collection
    """
    calendar_path = Path(base_path) / "collection-root" / user / calendar_name
    calendar_path.mkdir(parents=True, exist_ok=True)
    
    # Create .Radicale.props file for calendar properties
    props_file = calendar_path / ".Radicale.props"
    if not props_file.exists():
        props_content = f"""{{
  "C:supported-calendar-component-set": "VTODO,VEVENT",
  "D:displayname": "{calendar_name}",
  "tag": "VCALENDAR"
}}"""
        props_file.write_text(props_content, encoding="utf-8")
    
    return calendar_path


def create_todo(
    summary: str,
    description: str = "",
    priority: int = 0,
    status: str = "NEEDS-ACTION",
    due: datetime = None,
    uid: str = None
) -> Calendar:
    """
    Create a TODO calendar component.
    
    Args:
        summary: Todo title/summary
        description: Todo description
        priority: Priority (0=undefined, 1=highest, 9=lowest)
        status: Status (NEEDS-ACTION, COMPLETED, IN-PROCESS, CANCELLED)
        due: Due date
        uid: Unique identifier (auto-generated if not provided)
        
    Returns:
        Calendar object containing the TODO
    """
    cal = Calendar()
    cal.add('prodid', '-//Plane CalDAV Server//EN')
    cal.add('version', '2.0')
    
    todo = Todo()
    todo.add('summary', summary)
    
    if description:
        todo.add('description', description)
    
    if priority:
        todo.add('priority', priority)
    
    todo.add('status', status)
    
    if due:
        todo.add('due', due)
    
    # Add UID and timestamp
    todo.add('uid', uid or str(uuid.uuid4()))
    todo.add('dtstamp', datetime.now())
    
    cal.add_component(todo)
    return cal


def save_todo_to_file(calendar: Calendar, calendar_path: Path, filename: str = None) -> Path:
    """
    Save a TODO calendar to a file in the calendar collection.
    
    Args:
        calendar: Calendar object containing the TODO
        calendar_path: Path to the calendar collection directory
        filename: Filename to use (auto-generated if not provided)
        
    Returns:
        Path to the saved file
    """
    if filename is None:
        # Extract UID from the TODO component
        todo_component = None
        for component in calendar.walk():
            if component.name == "VTODO":
                todo_component = component
                break
        
        if todo_component and 'uid' in todo_component:
            uid = str(todo_component['uid'])
            filename = f"{uid}.ics"
        else:
            filename = f"{uuid.uuid4()}.ics"
    
    file_path = calendar_path / filename
    file_path.write_bytes(calendar.to_ical())
    return file_path


def add_todo_to_calendar(
    calendar_path: Path,
    summary: str,
    description: str = "",
    priority: int = 0,
    status: str = "NEEDS-ACTION",
    due: datetime = None,
    uid: str = None
) -> Path:
    """
    Create and save a TODO to a calendar collection.
    
    Args:
        calendar_path: Path to the calendar collection directory
        summary: Todo title/summary
        description: Todo description
        priority: Priority (0=undefined, 1=highest, 9=lowest)
        status: Status (NEEDS-ACTION, COMPLETED, IN-PROCESS, CANCELLED)
        due: Due date
        uid: Unique identifier (auto-generated if not provided)
        
    Returns:
        Path to the saved TODO file
    """
    cal = create_todo(summary, description, priority, status, due, uid)
    return save_todo_to_file(cal, calendar_path)


def list_todos(calendar_path: Path) -> list:
    """
    List all TODO files in a calendar collection.
    
    Args:
        calendar_path: Path to the calendar collection directory
        
    Returns:
        List of todo information dictionaries
    """
    todos = []
    
    for ics_file in calendar_path.glob("*.ics"):
        try:
            cal = Calendar.from_ical(ics_file.read_bytes())
            for component in cal.walk():
                if component.name == "VTODO":
                    todos.append({
                        'file': ics_file.name,
                        'uid': str(component.get('uid', '')),
                        'summary': str(component.get('summary', '')),
                        'status': str(component.get('status', 'NEEDS-ACTION')),
                        'priority': component.get('priority', 0),
                    })
        except Exception as e:
            print(f"Error reading {ics_file}: {e}")
    
    return todos
