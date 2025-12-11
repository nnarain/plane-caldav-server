#
# Function for interacting the Plane Project Management API
#
# @author Natesh Narain <nnaraindev@gmail.com>
#
import requests


class PlaneAPI:
    def __init__(self, url, api_key):
        self.api_key = api_key
        self._base_api_url = f"{url}/api/v1"

    def get_projects(self, workspace):
        json = self.get_projects_json(workspace)

        projects = []
        for project in json["results"]:
            project_id = project.get("id")
            project_name = project.get("name")

            projects.append({"id": project_id, "name": project_name})

        return projects

    def get_projects_json(self, workspace):
        url = f"{self._base_api_url}/workspaces/{workspace}/projects"
        headers = self._create_headers()
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_work_items(self, workspace, project_id):
        json = self.get_work_items_json(workspace, project_id)

        work_items = []
        for item in json["results"]:
            item_id = item.get("id")
            item_name = item.get("name")
            description = item.get("description_stripped")
            target_date = item.get("target_date")
            completed_at = item.get("completed_at")

            work_items.append(
                {
                    "id": item_id,
                    "name": item_name,
                    "description": description,
                    "target_date": target_date,
                    "completed_at": completed_at,
                }
            )

        return work_items

    def get_work_items_json(self, workspace, project_id):
        url = self._get_work_items_endpoint(workspace, project_id)
        headers = self._create_headers()
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def _create_headers(self):
        return {"X-API-Key": f"{self.api_key}"}

    def _get_work_items_endpoint(self, workspace, project):
        return f"{self._base_api_url}/workspaces/{workspace}/projects/{project}/work-items"
