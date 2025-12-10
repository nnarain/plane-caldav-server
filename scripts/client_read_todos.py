"""
CalDAV client to read and display TODOs from the server.
"""
from caldav import DAVClient
from datetime import datetime


def main():
    # Connect to the CalDAV server
    print("Connecting to CalDAV server...")
    client = DAVClient(
        "http://localhost:5232/",
        headers={"X-Remote-User": "testuser"}
    )
    
    # Get the principal (user)
    principal = client.principal()
    print(f"Connected as: {principal}")
    
    # Get all calendars
    calendars = principal.calendars()
    
    if not calendars:
        print("\nNo calendars found!")
        print("Run 'python setup_calendar.py' first to create a calendar with TODOs.")
        return
    
    # Display TODOs from each calendar
    for calendar in calendars:
        print(f"\n{'='*60}")
        print(f"Calendar: {calendar.name}")
        print('='*60)
        
        # Get all TODOs
        todos = calendar.todos()
        
        if not todos:
            print("  No TODOs found in this calendar.")
            continue
        
        print(f"Found {len(todos)} TODO(s):\n")
        
        for i, todo in enumerate(todos, 1):
            component = todo.vobject_instance.vtodo
            
            # Extract TODO properties
            summary = getattr(component, 'summary', 'No summary').value if hasattr(component, 'summary') else 'No summary'
            status = getattr(component, 'status', 'NEEDS-ACTION').value if hasattr(component, 'status') else 'NEEDS-ACTION'
            priority = getattr(component, 'priority', 0).value if hasattr(component, 'priority') else 0
            
            description = None
            if hasattr(component, 'description'):
                description = component.description.value
            
            due = None
            if hasattr(component, 'due'):
                due = component.due.value
            
            # Display TODO
            print(f"{i}. {summary}")
            print(f"   Status: {status}")
            print(f"   Priority: {priority}")
            if description:
                print(f"   Description: {description}")
            if due:
                print(f"   Due: {due}")
            print()


if __name__ == "__main__":
    main()
