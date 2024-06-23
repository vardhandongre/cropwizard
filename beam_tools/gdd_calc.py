import re
from typing import Any, Dict

import beam
import requests
from beam import App, QueueDepthAutoscaler, Runtime
from bs4 import BeautifulSoup

requirements = ["beautifulsoup4==4.12.3"]

app = App(
    "gdd_calc",
    runtime=Runtime(
        cpu=1,
        memory="2Gi",
        image=beam.Image(
            python_version="python3.10",
            python_packages=requirements,
        ),
    )
)

# Set up the GDD URL
url = 'https://warm.isws.illinois.edu/warm/cropdata/calcresult.asp'

# Set up the headers
headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Referer': 'https://warm.isws.illinois.edu/warm/cropdata/cropddcalc.asp'
}

# Cities mapping for placebox and areabox
cities = {
    "DeKalb": {"placebox": 5, "areabox": "dek"},
    "Freeport": {"placebox": 13, "areabox": "fre"},
    "St. Charles": {"placebox": 20, "areabox": "stc"},
    "Big Bend": {"placebox": 22, "areabox": "bbc"},
    "Stelle": {"placebox": 15, "areabox": "ste"},
    "Monmouth": {"placebox": 6, "areabox": "mon"},
    "Peoria": {"placebox": 8, "areabox": "icc"},
    "Snicarte": {"placebox": 16, "areabox": "sni"},
    "Champaign": {"placebox": 81, "areabox": "cmi"},
    "Bondville": {"placebox": 1, "areabox": "bvl"},
    "Perry": {"placebox": 4, "areabox": "orr"},
    "Springfield": {"placebox": 9, "areabox": "llc"},
    "Brownstown": {"placebox": 3, "areabox": "brw"},
    "Olney": {"placebox": 12, "areabox": "oln"},
    "Fairfield": {"placebox": 34, "areabox": "fai"},
    "Belleville": {"placebox": 10, "areabox": "frm"},
    "Rend Lake": {"placebox": 14, "areabox": "rnd"},
    "Carbondale": {"placebox": 11, "areabox": "siu"},
    "Dixon Springs": {"placebox": 2, "areabox": "dxs"},
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
    match = re.search(pattern, soup_text, re.DOTALL)
    if match:
        return match.group()
    else:
        return None

# Send the POST request to the GDD URL
def send_request(payload, pattern):
    try:
        response = requests.post(url, data=payload, headers=headers, timeout=20)
        print(f'Response status code: {response.status_code}')
        print(f'Response text: {response.text}')
        if response.status_code == 200:
            return parse_response(response, pattern)
        else:
            return f'Error: Received status code {response.status_code}'
    except requests.exceptions.RequestException as e:
        print(f'Error in sending request: {e}')
        return None

autoscaler = QueueDepthAutoscaler(max_tasks_per_replica=2, max_replicas=3)

@app.rest_api(
    max_pending_tasks=1_000,
    max_retries=3,
    timeout=60,
    autoscaler=autoscaler
)
def main(**inputs: Dict[str, Any]):
    print(f"Received inputs: {inputs}")
    
    base = inputs.get('base', '')
    date = inputs.get('date', '')
    plap = inputs.get('plap', '')
    print(base, date, plap)

    # Retrieve placebox and areabox from cities mapping
    city_info = cities.get(plap, {})
    placebox = city_info.get('placebox', '')
    areabox = city_info.get('areabox', '')

    if not placebox or not areabox:
        return {'error': f'City "{plap}" not found in the mapping.'}

    # Set up the payload
    payload_data = payload(base, placebox, areabox, date, plap)
    print(f'Payload data: {payload_data}')

    # Determine pattern based on base
    if base == '50':
        pattern = r"Corn growing\s+degree-days\s+at\s+{}\..*?Two-week:\s+\d+".format(plap)
    else:
        pattern = r"Crop growing\s+degree-days\s+\(base\s+40° F\)\s+at\s+{}\..*?Two-week:\s+\d+".format(plap)

    # Send the request
    response = send_request(payload_data, pattern)
    print(f"response {response}")

    if response:
        return {"response": response}
    else:
        return {'error': 'Error in getting response, got None'}
