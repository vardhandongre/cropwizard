# python script to send a POST request to url endpoint and get the response 
"""
To deploy: beam deploy crop_tool.py
For testing: beam serve crop_tool.py
Use CAII gmail to auth.
"""

import requests
from bs4 import BeautifulSoup
import json
import sys
import os
import time
import datetime
import re
from typing import Any, Dict
# import logging
# import logging.handlers
# import PIL
# from PIL import Image 

import beam
from beam import App, QueueDepthAutoscaler, Runtime
requirements = ["beautifulsoup4==4.12.3"]

# # Set up logging
# log = logging.getLogger('groundwater')
# log.setLevel(logging.DEBUG)
# handler = logging.FileHandler('logs/groundwater/groundwater.log')
# formatter = logging.Formatter('%(name)s: %(levelname)s %(message)s')
# handler.setFormatter(formatter)
# log.addHandler(handler)

app = App(
    "groundwater_tool",
    runtime=Runtime(
        cpu=1,
        memory="2Gi",
        image=beam.Image(
            python_version="python3.10",
            python_packages=requirements,
            # commands=["apt-get update && apt-get install -y ffmpeg tesseract-ocr"],
        ),
    ))

# Set up the url
city_to_well = {
    "Barry": 61,
    "Belleville": 10,
    "Big Bend": 22,
    "Bondville": 1120,
    "Bondville": 1,
    "Boyleston": 221,
    "Brownstown": 3,
    "Cambridge": 51,
    "Carbondale": 11,
    "Crystal Lake": 41,
    "Dekalb": 5,
    "Dixon Springs": 191,
    "Dixon Springs": 2,
    "Fairfield": 34,
    "Fermi": 53,
    "Freeport": 13,
    "Galena": 21,
    "Good Hope": 72,
    "Greenfield": 132,
    "Janesville": 143,
    "Kilbourne": 7,
    "Monmouth": 6,
    "Mt. Morris": 31,
    "Olney": 12,
    "Peoria": 8,
    "Perry": 4,
    "Rend Lake": 14,
    "S.E. Illinois College": 202,
    "Snicarte": 91,
    "Sparta / Eden": 171,
    "Springfield": 9,
    "St. Charles": 20,
    "St. Peter": 153,
    "Stelle": 15,
    "SWS": 181
}

# set up the headers
headers = {
    'Referer': 'https://warm.isws.illinois.edu/warm/groundwater/'
}

# Setup dynamic payload
def payload(city):
    return{
        'well': str(city_to_well[city])
    }
    
# Parse the response
def fetch_and_parse_response(response):
    soup = BeautifulSoup(response.text, 'html.parser')
    soup_text = soup.get_text()
    pattern = r"addRow\(\[new Date\((\d{4}) ,(\d{1,2}) ,(\d{1,2})\), (\d+\.\d+)\]\);"
    matches = re.findall(pattern, response.text)
    # log.info(f"Response: {soup}")
    data = {(int(year), int(month)): float(depth) for year, month, day, depth in matches}
    # log.info(data)
    return data

# get the depth value
def get_depth(data, month, year):
    if type(month) == int:
        month_num = month - 1
    else:
        month_num = datetime.datetime.strptime(month, "%B").month - 1
    return data.get((year, month_num))

# Send a GET request to the url
def fetch_depth(city, month, year):
    # Set up the url
    well_id = city_to_well[city]
    if not well_id:
        log.error(f"City {city} not found")
        return None
    url = f"https://warm.isws.illinois.edu/warm/groundwater/station.asp?well={well_id}"
    response = requests.get(url, data=payload(city), headers=headers)
    if response.status_code != 200:
        print("Failed to fetch the webpage")
        log.error(f"Failed to fetch the webpage. Status code: {response.status_code}")
        return None
    data = fetch_and_parse_response(response)
    return get_depth(data, month, year)



autoscaler = QueueDepthAutoscaler(max_tasks_per_replica=2, max_replicas=3)

# @app.task_queue(
@app.rest_api(
    # workers=1,
    # callback_url is used for 'in progress' & 'failed' tracking. But already handeled by other Beam endpoint.
    # callback_url='https://uiuc-chat-git-ingestprogresstracking-kastanday.vercel.app/api/UIUC-api/ingestTaskCallback',
    max_pending_tasks=1_000,
    max_retries=3,
    timeout=60,
    # loader=loader,
    autoscaler=autoscaler)
# Main function
def main(**inputs: Dict[str, Any]):
    city = inputs.get('city', '')
    month = inputs.get('month', '')
    year = inputs.get('year', '')
    depth = fetch_depth(city, month, year)
    if depth:
        response = {"response": f"The depth of groundwater in {city} for {month} {year} is {depth} ft"}
        print(f"{response}")
        return json.dumps(response)
        # log.info(f"The depth of groundwater in {city} for {month} {year} is {depth} ft")
    else:
        print("Failed to fetch the depth of groundwater")
        # log.error("Failed to fetch the depth of groundwater")
        sys.exit(1)

