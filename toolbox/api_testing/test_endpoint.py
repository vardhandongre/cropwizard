# from flask import Flask

# app = Flask(__name__)

# @app.route('/')
# def home():
#     return 'Welcome to the home page!'

# @app.route('/greet')
# def greet():
#     return 'Hello, World!'

# if __name__ == '__main__':
#     app.run(debug=True)


from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import re
import logging

# Set up logging
log = logging.getLogger('seasonal_maps')
log.setLevel(logging.DEBUG)
handler = logging.FileHandler('logs/map/map.log')
formatter = logging.Formatter('%(name)s: %(levelname)s %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)

app = Flask(__name__)

# Set up the URL and headers
URL = "https://warm.isws.illinois.edu/warm/warm_pdd/default.aspx"
HEADERS = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Referer': 'https://warm.isws.illinois.edu/warm/warm_pdd/default.aspx'
}

# Initial request to get VIEWSTATE data
session = requests.Session()
response = session.get(URL)
soup = BeautifulSoup(response.text, 'html.parser')
VIEWSTATE = soup.find(id="__VIEWSTATE")['value']
EVENTVALIDATION = soup.find(id="__EVENTVALIDATION")['value']
VIEWSTATEGENERATOR = soup.find(id="__VIEWSTATEGENERATOR")['value']

def create_payload(type):
    # Setup dynamic payload
    if type == 'japanese_beetle':
        return {
            '__VIEWSTATE': VIEWSTATE,
            '__VIEWSTATEGENERATOR': VIEWSTATEGENERATOR,
            '__EVENTVALIDATION': EVENTVALIDATION,
            'JBMap': 'Japanese Beetle Map'
        }
    elif type == 'corn_flea_beetle':
        return {
            '__VIEWSTATE': VIEWSTATE,
            '__VIEWSTATEGENERATOR': VIEWSTATEGENERATOR,
            '__EVENTVALIDATION': EVENTVALIDATION,
            'CFBMap': 'Corn Flea Beetle Map'
        }
    elif type == 'brown_marmorated_stinkbug':
        return {
            '__VIEWSTATE': VIEWSTATE,
            '__VIEWSTATEGENERATOR': VIEWSTATEGENERATOR,
            '__EVENTVALIDATION': EVENTVALIDATION,
            'BMSMap': 'Brown Marmorated Stinkbug Map'
        }
    else:
        return None

@app.route('/get_pest_info', methods=['POST'])
def get_pest_info():
    request_data = request.get_json()
    pest_type = request_data.get('type', '')
    payload = create_payload(pest_type)
    
    if not payload:
        return jsonify({'error': 'Invalid pest type'}), 400
    
    # Define patterns based on pest type
    pattern = {
        'japanese_beetle': r"Japanese\s+Beetle\s+.*?DDs",
        'corn_flea_beetle': r"Corn\s+Flea\s+Beetle\s+Degree\s+Days\s+Map\s+for\s+Illinois\s+at\s+.*?Two-week:\s+\d+",
        'brown_marmorated_stinkbug': r"Brown\s+Marmorated\s+Stinkbug\s+Degree\s+Days\s+Map\s+for\s+Illinois\s+at\s+.*?Two-week:\s+\d+"
    }.get(pest_type, '')

    try:
        response = requests.post(URL, data=payload, headers=HEADERS)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            match = re.search(pattern, soup.get_text(), re.DOTALL)
            map_link = f"https://warm.isws.illinois.edu/warm/warm_pdd/images/{pest_type.replace('_', '')}_Map.svg"
            return jsonify({'response': match.group(0) if match else 'No data found', 'map_link': map_link})
    except requests.exceptions.RequestException as e:
        log.error(f'Error in sending request: {e}')
        return jsonify({'error': 'Failed to fetch data'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
