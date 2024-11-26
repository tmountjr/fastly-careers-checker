import re
import json
from os import path

import requests
from deepdiff import DeepDiff

MANIFEST_PATH = path.join(
    path.dirname(path.realpath(__file__)),
    "manifest.json"
)
CAREERS_URL = "https://api.greenhouse.io/v1/boards/fastly/embed/departments"

session = requests.session()

# Load manifest.json.
with open(MANIFEST_PATH, "r", encoding="utf-8") as manifest_handle:
    manifest = json.loads(manifest_handle.read())

try:
    response = session.request("get", CAREERS_URL)
    response.raise_for_status()
    new_data = json.loads(response.text)
except requests.exceptions.RequestException as e:
    print(f"Error fetching URL: {e}")

def simplify_job(j) -> dict[str, str]:
    """Returns a simplified job object from an API job.
    """
    return {
        "url": j["absolute_url"],
        "location": j["location"]["name"],
        "title": j["title"]
    }

# Create a hash table where the key is the top-level department id
# and the value is a dictionary of name and jobs
postings = {}
for department in new_data["departments"]:
    dept_id = department["id"]
    parent_id = department["parent_id"]
    jobs_to_add = [ simplify_job(x) for x in department["jobs"] ]

    if parent_id is None:
        if dept_id in postings:
            # stub, overwrite name and merge jobs
            postings[dept_id]["name"] = department["name"]
            postings[dept_id]["jobs"] += jobs_to_add
        else:
            # new entry
            postings[dept_id] = {
                "name": department["name"],
                "jobs": jobs_to_add
            }
    else:
        if parent_id in postings:
            # update existing parent department jobs
            postings[parent_id]["jobs"] += jobs_to_add
        else:
            # stub out new entry for parent department
            postings[parent_id] = {
                "name": "PENDING",
                "jobs": jobs_to_add
            }

diff = DeepDiff(
    manifest,
    json.loads(json.dumps(postings)),
    threshold_to_diff_deeper=0.8
)
if "iterable_item_added" in diff:
    added = diff["iterable_item_added"]

    new_jobs_posted = []
    for key in added.keys():
        chunks = re.findall(r"'(.*?)'|\[(\d+)\]", key)
        dept_id, key, index = [ item for sublist in chunks for item in sublist if item ]
        dept_id = int(dept_id)
        index = int(index)
        job = postings[dept_id][key][index]
        dept_name = postings[dept_id]["name"]
        title = job["title"]
        location = job["location"]
        new_jobs_posted.append(
            f'New job posted in "{dept_name}": {title} based in {location}.'
        )

    print(new_jobs_posted)
else:
    print("No new jobs posted.")

with open(MANIFEST_PATH, "w+", encoding="utf-8") as manifest_handle:
    manifest_handle.write(json.dumps(postings, indent=2))
