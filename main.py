import re
import json
import requests
from deepdiff import DeepDiff

CAREERS_URL = "https://api.greenhouse.io/v1/boards/fastly/embed/departments"

session = requests.session()

# Load manifest.json.
with open("./manifest.json", "r", encoding="utf-8") as manifest_handle:
    manifest = json.loads(manifest_handle.read())

try:
    response = session.request("get", CAREERS_URL)
    response.raise_for_status()
    new_data = json.loads(response.text)
except requests.exceptions.RequestException as e:
    print(f"Error fetching URL: {e}")

def simplify_job(j):
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

    if parent_id is None:
        if dept_id in postings:
            # stub, overwrite name and merge jobs
            postings[dept_id]["name"] = department["name"]
            postings[dept_id]["jobs"] += [ simplify_job(x) for x in department["jobs"] ]
        else:
            # new entry
            postings[dept_id] = {
                "name": department["name"],
                "jobs": [ simplify_job(x) for x in department["jobs"] ]
            }
    else:
        if parent_id in postings:
            # update existing parent department jobs
            postings[parent_id]["jobs"] += [ simplify_job(x) for x in department["jobs"] ]
        else:
            # stub out new entry for parent department
            postings[parent_id] = {
                "name": "PENDING",
                "jobs": [ simplify_job(x) for x in department["jobs"] ]
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
        new_jobs_posted.append(
            f'New job posted in "{dept_name}": {job["title"]} based in {job["location"]}.'
        )

    print(new_jobs_posted)
else:
    print("no new jobs posted.")
