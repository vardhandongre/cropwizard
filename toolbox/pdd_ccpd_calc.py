import requests
from bs4 import BeautifulSoup

# Define the URL for the request
url = "https://warm.isws.illinois.edu/warm/warm_pdd/default.aspx"

# Define the headers for the request
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": "https://warm.isws.illinois.edu/warm/warm_pdd/default.aspx",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": "https://warm.isws.illinois.edu",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1"
}

# Mapping of city names to their corresponding option values
station_mapping = {
    "Belleville": 10,
    "Big Bend": 22,
    "Bondville": 1,
    "Brownstown": 3,
    "Carbondale": 11,
    "Champaign": 81,
    "DeKalb": 5,
    "Dixon Springs": 2,
    "Fairfield": 34,
    "Freeport": 13,
    "Monmouth": 6,
    "Olney": 12,
    "Peoria": 8,
    "Perry": 4,
    "Rend Lake": 14,
    "Snicarte": 16,
    "Springfield": 9,
    "St Charles": 20,
    "Stelle": 15
}

def fetch_dynamic_values_and_form_fields(session, url):
    # Fetch the initial page to get the dynamic values
    initial_response = session.get(url)
    initial_soup = BeautifulSoup(initial_response.text, 'html.parser')

    # Extract all hidden fields
    hidden_fields = initial_soup.find_all("input", type="hidden")
    form_data = {}
    for field in hidden_fields:
        form_data[field.get("name")] = field.get("value")
    
    return form_data

def send_post_request(station, pest, bio_fix_date):
    with requests.Session() as session:
        # Fetch dynamic values
        form_data = fetch_dynamic_values_and_form_fields(session, url)

        # Set cookies from the network tab
        cookies = {
            "ASP.NET_SessionId": "msytvzhm1gumdwmxe50xuc2",
            "ASPSessionIDQCCG": "KLAKICCCJIECHJAPOIGBIFIO",
            "ASPSessionIDSECBBAC": "IIDBGBMABDOGPNJNMPFCDOBNA",
            "OptanonAlertBoxClosed": "2024-05-31T16:46:43.598Z",
            "OptanonConsent": "isGpcEnabled=0&datestamp=Fri+May+31+2024+11%3A46%3A44+GMT-0500+(Central+Daylight+Time)&version=6.39.0&geolocation=%3B&isIABGlobal=false&hosts=&consentId=&interactionCount=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1%2CC0005%3A1&AwaitingReconsent=false&cmpId=",
            "__utma": "87658782.824964944.1716589901.1717474400.1717474400.1",
            "__utmc": "87658782",
            "__utmz": "87658782.1716757558.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)",
            "_ga": "GA1.1.824964944.1716589901",
            "_ga_3PMEZWw88R": "GS1.1.1716686319.3.0.1716686319.0.0.0",
            "_ga_55Y7R0N4FV": "GS1.1.1717472795.1.1.1717472810.0.0.0",
            "_ga_5K2RGDXG9P": "GS1.1.1717083527.4.1.1717083696.0.0.0",
            "_ga_6P9Y2BXVK4": "GS1.1.1716590108.10.1.1716590110.0.0.0",
            "_ga_71JGWHBFGH": "GS1.1.1714689460.2.1.1714689463.57.0.0",
            "_ga_8NR8L2FCE3": "GS1.1.1717081883.10.1.1717081885.0.0.0",
            "_ga_G1PL9SWPDXYH": "GS1.1.1714671737.1.1.1714671749.48.0.0",
            "_ga_RLMMW68LGH": "GS1.1.1713192673.2.0.1713192673.0.0.0",
            "_ga_R0ZHZBODCM": "GS1.1.1714679228.2.1.1714679240.29.0.0",
            "_ga_TWFEJJKL35": "GS1.1.1717174003.2.0.1717174004.59.0.0",
            "_ga_V2MJZVPFIL": "GS1.1.1715186018.1.1.1715186030.52.0.0",
            "_ga_X7QVZSE1FK": "GS1.1.1714673732.2.1.1714673744.0.0.0",
            "stationID": "cmi"
        }
        session.cookies.update(cookies)

        # Convert station name to station ID
        station_id = station_mapping.get(station)
        if station_id is None:
            print(f"Error: Invalid station name '{station}'")
            return

        # Update form data with user inputs
        form_data.update({
            'StationsDDL': str(station_id),
            'PestsDDL': str(pest),
            'UserBioFixDate': str(bio_fix_date),
            'CalculateButton': 'Calculate'
        })
        
        print("Form Data:", form_data)  # Debug: Print all form fields to verify

        # Send the POST request
        response = session.post(url, headers=headers, data=form_data)

        # Check if the request was successful
        if response.status_code == 200:
            print("Request was successful!")
        else:
            print(f"Request failed with status code {response.status_code}")
            print(response.text)

# User input
station = input("Enter the station name (e.g., Belleville, Big Bend, Bondville, etc.): ")
pest = input("Enter the pest: ")
bio_fix_date = input("Enter the bio fix date (YYYY-MM-DD): ")

# Ensure the pest name matches the expected format exactly
pest = pest.strip()  # Remove any extra whitespace

# Send the request with user input
send_post_request(station, pest, bio_fix_date)
