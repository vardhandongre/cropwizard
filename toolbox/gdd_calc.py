# python script to send a POST request to GDD url endpoint and gett the response
import requests
from bs4 import BeautifulSoup
import json
import sys
import os
import time
import datetime
import re
import logging
import logging.handlers

# Set up logging
log = logging.getLogger('gdd_calc')
log.setLevel(logging.DEBUG)
# handler = logging.handlers.SysLogHandler(address = '/dev/log')
handler = logging.FileHandler('logs/gdd_calc/gdd.log')
formatter = logging.Formatter('%(name)s: %(levelname)s %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)

# Set up the GDD URL
url = 'https://warm.isws.illinois.edu/warm/cropdata/calcresult.asp'

# Set up the headers
headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Referer': 'https://warm.isws.illinois.edu/warm/cropdata/cropddcalc.asp'
}

# Set up the dynamic payload
def payload(base, placebox, areabox, date, plap):
    return{
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
        response = requests.post(url, data = payload, headers = headers)
        if response.status_code == 200:
            return parse_response(response, pattern)
    except requests.exceptions.RequestException as e:
        log.error(f'Error in sending request: {e}')
        return None
    
# Main function
def main():
    # Set up the payload
    base = input('Enter the base temperature: ')
    placebox = input('Enter the placebox: ')
    areabox = input('Enter the areabox: ')
    date = input('Enter the date: ')
    plap = input('Enter the plap: ')
    payload_data = payload(base, placebox, areabox, date, plap)
    log.info(f'Payload data: {payload_data}')
    if base == 50:
        pattern = r"Corn growing\s+degree-days\s+at\s+{}\..*?Two-week:\s+\d+".format(plap)
    else:
        pattern = r"Crop growing\s+degree-days\s+\(base\s+40° F\)\s+at\s+{}\..*?Two-week:\s+\d+".format(plap)
    # Send the request
    response = send_request(payload_data, pattern)
    print(response)
    # Log the response
    if response:
        log.info(f'Response: {response}')
    else:
        log.error('Error in getting response')
        sys.exit(1)
        
if __name__ == '__main__':
    main()
    
    
            