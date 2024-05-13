import requests
from bs4 import BeautifulSoup
import re
import logging
import sys

# Set up logging
def setup_logging():
    log = logging.getLogger('gdd_calc')
    log.setLevel(logging.DEBUG)
    handler = logging.FileHandler('logs/gdd_calc/gdd.log')
    formatter = logging.Formatter('%(name)s: %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    return log

# Define the main function to handle GDD response
def get_gdd_response(base, placebox, areabox, date, plap):
    log = setup_logging()
    url = 'https://warm.isws.illinois.edu/warm/cropdata/calcresult.asp'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': 'https://warm.isws.illinois.edu/warm/cropdata/cropddcalc.asp'
    }

    # Payload preparation
    payload = {
        'base': str(base),
        'placebox': str(placebox),
        'areabox': str(areabox),
        'date': str(date),
        'plap': str(plap)
    }
    log.info(f'Payload data: {payload}')
    
    # Pattern based on base temperature
    if base == 50:
        pattern = r"Corn growing\s+degree-days\s+at\s+{}\..*?Two-week:\s+\d+".format(plap)
    else:
        pattern = r"Crop growing\s+degree-days\s+\(base\s+40° F\)\s+at\s+{}\..*?Two-week:\s+\d+".format(plap)

    try:
        response = requests.post(url, data=payload, headers=headers)
        if response.status_code == 200:
            # Parse the response
            soup = BeautifulSoup(response.text, 'html.parser')
            soup_text = soup.get_text()
            match = re.search(pattern, soup_text, re.DOTALL)
            if match:
                result = match.group()
                log.info(f'Response: {result}')
                return result
            else:
                log.error('No match found in response')
                return None
        else:
            log.error(f'HTTP Error: {response.status_code}')
            return None
    except requests.exceptions.RequestException as e:
        log.error(f'Request exception: {e}')
        return None

# Example of using the function
if __name__ == '__main__':
    base = input('Enter the base temperature: ')
    placebox = input('Enter the placebox: ')
    areabox = input('Enter the areabox: ')
    date = input('Enter the date: ')
    plap = input('Enter the plap: ')

    result = get_gdd_response(base, placebox, areabox, date, plap)
    if result:
        print(result)
    else:
        print('Failed to get a valid response.')
        sys.exit(1)
