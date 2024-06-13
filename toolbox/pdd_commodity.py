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
# import PIL
# from PIL import Image 
# Set up logging
# log = logging.getLogger('pdd_commodity')
# log.setLevel(logging.DEBUG)
# handler = logging.FileHandler('logs/pddc/pddc.log')
# formatter = logging.Formatter('%(name)s: %(levelname)s %(message)s')
# handler.setFormatter(formatter)
# log.addHandler(handler)

# City to station mapping
city_to_station = {
    'Belleville': 10,
    'Big Bend': 22,
    'Bondville': 1,
}

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
def payload(pest, city, date):
    return{
        '__VIEWSTATE': viewstate,
        '_VIEWSTATEGENERATOR': viewstategenerator,
        '__EVENTVALIDATION': eventvalidation,
        'StationsDDL': city_to_station[city],
        'PestsDDL': pest,
        'UserBioFixDate': date,
        'CalculateButton': 'Calculate'
    }

# Send the POST request
def send_request(payload):
    response = session.post(url, headers=headers, data=payload)
    return response


# Main function
def main():
    pest = input("Enter the pest: ")
    city = input("Enter the city: ")
    date = input("Enter the date in yyyy-mm-dd: ")
    payload_data = payload(pest, city, date)
    response = send_request(payload_data)
    print(payload_data)
    print(response)
    if response.status_code != 200:
        print("Failed to fetch the webpage")
        # log.error(f"Failed to fetch the webpage. Status code: {response.status_code}")
        sys.exit(1)
    # soup = BeautifulSoup(response.text, 'html.parser')
    # # Extract the image url
    # img_url = soup.find('img', {'id': 'PDDMap'})['src']
    # # Download the image
    # img_response = session.get(img_url)
    # img = Image.open(BytesIO(img_response.content))
    # img.save(f"images/{pest}_{city}.png")
    # print(f"Image saved as {pest}_{city}.png")
    # log.info(f"Image saved as {pest}_{city}.png")


if __name__ == '__main__':
    main()