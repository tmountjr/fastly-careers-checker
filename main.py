import json
import requests

CAREERS_URL = "https://www.fastly.com/about/careers/current-openings"

# Data is structured like this:
# div#job-list is the main list of jobs
#   child divs[data-testid="department"] nodes are categories
#     within each category, h3 contains the category name
#     child divs after h3 are all the open jobs
#       within each child div,
#           a element has:
#             * href to JD
#             * name of position is text content
#           p element has location
#
# potential JSON structure in manifest.json
#
# Dictionary comparison as sets: https://stackoverflow.com/a/60935162
#
# Process:
# 1. read in manifest.json as dictionary
# 2. scrape CAREERS_URL
# 3. parse with bs4
# 4. pick out div#job-list
# 5. crawl through div and generate a new dict with the current data
# 6. do a deep set comparison between the manifest and what was crawled. Print any additions.
# 7. save the new crawl response to manifest.json.

with open("./manifest.json", "r", encoding="utf-8") as manifest:
    old_manifest = json.loads(manifest.read())
