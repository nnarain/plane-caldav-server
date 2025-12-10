from caldav import DAVClient
from icalendar import Todo

# Connect with X-Remote-User header for http_x_remote_user auth
client = DAVClient(
    "http://localhost:5232/",
    headers={"X-Remote-User": "testuser"}
)
principal = client.principal()
calendars = principal.calendars()

for calendar in calendars:
    print("Calendar:", calendar)
    todos = calendar.todos()
    for todo in todos:
        print("--- TODO ---")
        component = todo.vobject_instance
        print(component)
