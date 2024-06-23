import os
import re
import sys
import time
import json
import yaml
import logging
import requests
import datetime
import logging.handlers
from bs4 import BeautifulSoup
import beam
from beam import App, Runtime, Image, QueueDepthAutoscaler

requirements = ["beautifulsoup4==4.12.3"]

app = App(
    name="inference-quickstart",
    runtime=Runtime(
        cpu=1,
        memory="8Gi",
        gpu="T4",
        image=Image(
            python_version="python3.10",
            python_packages=[
                requirements,
            ],  # You can also add a path to a requirements.txt instead
        ),
    ),
)


# # Set up logging
# log = logging.getLogger('gdd_calc')
# log.setLevel(logging.DEBUG)
# handler = logging.FileHandler('logs/gdd_calc/gdd.log')
# formatter = logging.Formatter('%(asctime)s %(name)s: %(levelname)s %(message)s')
# handler.setFormatter(formatter)
# log.addHandler(handler)

# Set up the GDD URL
url = 'https://warm.isws.illinois.edu/warm/cropdata/calcresult.asp'

# Set up the headers
headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Referer': 'https://warm.isws.illinois.edu/warm/cropdata/cropddcalc.asp'
}

# Set up the dynamic payload
def payload(base, placebox, areabox, date, plap):
    return {
        'base': str(base),
        'placebox': str(placebox),
        'areabox': str(areabox),
        'date': str(date),
        'plap': str(plap)
    }

# Parse the response using regex
def parse_response(response, pattern):
    soup = BeautifulSoup(response.text, 'html.parser')
    soup_text = soup.get_text()
    # log.debug(f"Soup text: {soup_text}")
    match = re.search(pattern, soup_text, re.DOTALL)
    if match:
        return match.group()
    else:
        return None

# Send the POST request to the GDD URL
def send_request(payload, pattern):
    try:
        response = requests.post(url, data=payload, headers=headers)
        # log.info(f"Response status code: {response.status_code}")
        # log.debug(f"Response text: {response.text}")
        if response.status_code == 200:
            return parse_response(response, pattern)
        else:
            # log.error(f"Failed to get a valid response: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        # log.error(f'Error in sending request: {e}')
        return None

def hidden_parameters(plap, cities):
    if plap in cities:
        placebox = cities[plap]['placebox']
        areabox = cities[plap]['areabox']
        return placebox, areabox
    else:
        # log.error(f'City "{plap}" not found in the file')
        sys.exit(1)



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
def main():
    # Load .yml file
    with open('gdd_plap.yml', 'r') as file:
        data = yaml.safe_load(file)
        cities = data['cities']  # Access the nested 'cities' key

    # Set up the payload
    base = input('Enter the base temperature: ')
    date = input('Enter the date: ')
    plap = input('Enter the city: ')

    placebox, areabox = hidden_parameters(plap, cities)

    payload_data = payload(base, placebox, areabox, date, plap)
    # log.info(f'Payload data: {payload_data}')

    if base == '50':
        pattern = r"Corn growing\s+degree-days\s+at\s+{}\..*?Two-week:\s+\d+".format(plap)
    else:
        pattern = r"Crop growing\s+degree-days\s+\(base\s+40° F\)\s+at\s+{}\..*?Two-week:\s+\d+".format(plap)

    # Send the request
    response = send_request(payload_data, pattern)
    if response:
        print(response)
        # log.info(f'Response: {response}')
    else:
        print('No response received or error occurred.')
        # log.error('Error in getting response')
        sys.exit(1)

if __name__ == '__main__':
    main()
