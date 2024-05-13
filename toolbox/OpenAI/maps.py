import requests
from bs4 import BeautifulSoup
import re
import sys

def fetch_map_data(pest_type):
    url = "https://warm.isws.illinois.edu/warm/warm_pdd/default.aspx"
    session = requests.Session()
    response = session.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract the state management fields
    viewstate = soup.find(id="__VIEWSTATE")['value']
    eventvalidation = soup.find(id="__EVENTVALIDATION")['value']
    viewstategenerator = soup.find(id="__VIEWSTATEGENERATOR")['value']
    
    # Headers and payload based on pest type
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': url
    }

    payload = {
        '__VIEWSTATE': viewstate,
        '__VIEWSTATEGENERATOR': viewstategenerator,
        '__EVENTVALIDATION': eventvalidation,
    }

    # Define pest-specific values
    pest_maps = {
        'japanese_beetle': 'JBMap',
        'corn_flea_beetle': 'CFBMap',
        'brown_marmorated_stinkbug': 'BMSMap'
    }
    pest_map_value = {
        'japanese_beetle': 'Japanese Beetle Map',
        'corn_flea_beetle': 'Corn Flea Beetle Map',
        'brown_marmorated_stinkbug': 'Brown Marmorated Stinkbug Map'
    }

    if pest_type in pest_maps:
        payload[pest_maps[pest_type]] = pest_map_value[pest_type]
    else:
        print('Invalid type of pest')
        sys.exit(1)

    response = session.post(url, data=payload, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        map_link = f"https://warm.isws.illinois.edu/warm/warm_pdd/images/{pest_maps[pest_type]}_Map.svg"
        return map_link
    else:
        return None

if __name__ == '__main__':
    pest_type = input('Enter the type of pest (japanese_beetle, corn_flea_beetle, brown_marmorated_stinkbug): ')
    map_link = fetch_map_data(pest_type)
    if map_link:
        print(f"Map link: {map_link}")
    else:
        print('Failed to get a valid response.')
