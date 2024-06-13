import requests
from bs4 import BeautifulSoup

# URL of the webpage
url = 'https://warm.isws.illinois.edu/warm/stationmeta.asp?site=FRM&from=sl'

# Headers to mimic the browser request
headers = {
    'Content-Type': 'text/html',
    'Referer': 'https://warm.isws.illinois.edu/warm/soil/'
}

# Send POST request
def send_request(payload):
    try:
        response = requests.post(url, data = payload, headers = headers)
        if response.status_code == 200:
            return response
    except requests.exceptions.RequestException as e:
        print(f'Error in sending request: {e}')
    return None

# Main function
def main():
    # Set up the payload
    payload = {
        'site': 'FRM',
        'from': 'sl'
    }
    response = send_request(payload)
    if response:
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()
    

        print(text)
    else:
        print("Failed to fetch the webpage")

if __name__ == "__main__":
    