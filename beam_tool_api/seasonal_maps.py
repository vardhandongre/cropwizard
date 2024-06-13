# python script to send a POST request to default.aspx url endpoint and get the response
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

# Set up logging
# log = logging.getLogger('seasonal_maps')
# log.setLevel(logging.DEBUG)
# handler = logging.FileHandler('logs/map/map.log')
# formatter = logging.Formatter('%(name)s: %(levelname)s %(message)s')
# handler.setFormatter(formatter)
# log.addHandler(handler)

app = App(
    "pest_seasonal_maps_tool",
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
url = "https://warm.isws.illinois.edu/warm/warm_pdd/default.aspx"
session = requests.Session()
response = session.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Extract the state management fields
viewstate = soup.find(id="__VIEWSTATE")['value']
eventvalidation = soup.find(id="__EVENTVALIDATION")['value']
viewstategenerator = soup.find(id="__VIEWSTATEGENERATOR")['value']

# Set up the headers
headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Referer': 'https://warm.isws.illinois.edu/warm/warm_pdd/default.aspx'
}

# Setup dynamic payload
def payload(type):
    if type == 'japanese_beetle':
        return{
            '__VIEWSTATE': viewstate,
            '_VIEWSTATEGENERATOR': viewstategenerator,
            '__EVENTVALIDATION': eventvalidation,
            'JBMap': 'Japanese Beetle Map'
        }
    elif type == 'corn_flea_beetle':
        return{
            '__VIEWSTATE': viewstate,
            '_VIEWSTATEGENERATOR': viewstategenerator,
            '__EVENTVALIDATION': eventvalidation,
            'CFBMap': 'Corn Flea Beetle Map'
        }
    elif type == 'brown_marmorated_stinkbug':
        return{
            '__VIEWSTATE': viewstate,
            '_VIEWSTATEGENERATOR': viewstategenerator,
            '__EVENTVALIDATION': eventvalidation,
            'BMSMap': 'Brown Marmorated Stinkbug Map'
        }
    else:
        return None
        
# Parse the response
def parse_response(response, pattern, type):
    soup = BeautifulSoup(response.text, 'html.parser')
    soup_text = soup.get_text()
    match = re.search(pattern, soup_text, re.DOTALL)
    
    # return the match and the link to map
    if type == 'japanese beetle':
        return match.group(), 'https://warm.isws.illinois.edu/warm/warm_pdd/images/JB_PestDegreeDaysMap.svg'
    elif type == 'corn flea beetle':
        table = soup.find('table')
        if table:
            # Iterate over all rows in the found table
            for row in table.find_all('tr'):
                # Extract columns from the row
                columns = row.find_all('td')  # Use 'td' for table data cells, 'th' if you need headers
                
                # Get text from each column and create a list of column texts
                column_texts = [col.get_text(strip=True) for col in columns]
                
                # Print the columns separated by a tab for better readability
                print('\t'.join(column_texts))
        else:
            print("No table found.")
        return 'https://warm.isws.illinois.edu/warm/warm_pdd/images/CFB_Map.svg'
    
    elif type == 'brown marmorated stinkbug':
        table = soup.find('table')
        if table:
            # Iterate over all rows in the found table
            for row in table.find_all('tr'):
                # Extract columns from the row
                columns = row.find_all('td')  # Use 'td' for table data cells, 'th' if you need headers
                
                # Get text from each column and create a list of column texts
                column_texts = [col.get_text(strip=True) for col in columns]
                
                # Print the columns separated by a tab for better readability
                print('\t'.join(column_texts))
        else:
            print("No table found.")
        return 'https://warm.isws.illinois.edu/warm/warm_pdd/images/BMS_Map.svg'
    else:
        return None
    
# Send the POST request
def send_request(payload, pattern, type):
    try:
        response = requests.post(url, data = payload, headers = headers)
        if response.status_code == 200:
            return parse_response(response, pattern, type)
    except requests.exceptions.RequestException as e:
        # log.error(f'Error in sending request: {e}')
        return None
    
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
    # Set up the payload
    type = inputs.get('pest','')
    type = type.lower()
    print(type)
    if type == 'japanese beetle':
        # print("yes")
        payload_data = payload('japanese_beetle')
        pattern = r"Japanese\s+Beetle\s+.*?DDs"
    elif type == 'corn flea beetle':
        payload_data = payload('corn_flea_beetle')
        pattern = r"Corn\s+Flea\s+Beetle\s+Degree\s+Days\s+Map\s+for\s+Illinois\s+at\s+.*?Two-week:\s+\d+"
    elif type == 'brown marmorated stinkbug':
        payload_data = payload('brown_marmorated_stinkbug')
        pattern = r"Brown\s+Marmorated\s+Stinkbug\s+Degree\s+Days\s+Map\s+for\s+Illinois\s+at\s+.*?Two-week:\s+\d+"
    else:
        # log.error('Invalid type of pest')
        sys.exit(1) 
    
    # log.info(f'Payload data: {payload_data}')
    # Send the request
    response = send_request(payload_data, pattern, type)
    print(f"response: {response}")
    # Log the response
    if response:
        if type == 'japanese beetle':
            map_data = requests.get(response[1])
            print("Response: ", response[0])
            print("Map link: ", response[1])
            result = {"response": f"{response[0]}", "map_link": f"{response[1]}"}
            return json.dumps(result)
            # log.info(f'Response: {response[0]}')
            # log.info(f'Map link: {response[1]}')
            
        else:
            map_data = requests.get(response)
            print("Map link: ", response)
            result = {"map_link": f"{response}"}
            return json.dumps(result)
            # log.info(f'Map link: {response}')
    else:
        # log.error('Error in getting response')
        sys.exit(1)
    
        
    # Save the map svg from link to a file
    
    # with open('logs/map/map.svg', 'wb') as f:
    #     f.write(map_data.content)
    #     f.close()
    #     log.info('Map saved successfully')

