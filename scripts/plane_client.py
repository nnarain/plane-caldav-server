import sys
from pathlib import Path
from argparse import ArgumentParser

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from plane_caldav_server.plane import PlaneAPI

def main(args):
    pass

if __name__ == "__main__":
    parser = ArgumentParser(description="Plane Project Management API Client")
    parser.add_argument("--url", required=True, help="Base URL of the Plane server")
    parser.add_argument("--api-key", required=True, help="API key for authentication")
    parser.add_argument("--workspace", required=True, help="Workspace ID")
    
    args = parser.parse_args()
    api = PlaneAPI(args.url, args.api_key)
    
    print("Fetching projects...")
    projects = api.get_projects(args.workspace)
    print(projects)
    
    # print("\nFetching work items...")
    for project in projects:
        print(f"\nWork items for project: {project['name']}")
        work_items = api.get_work_items(args.workspace, project["id"])
        print(work_items)