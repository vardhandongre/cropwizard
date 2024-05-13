import requests
from bs4 import BeautifulSoup
import re
import datetime
import logging

# Configure logging
def configure_logging():
    log = logging.getLogger('groundwater')
    log.setLevel(logging.DEBUG)
    handler = logging.FileHandler('logs/groundwater/groundwater.log')
    formatter = logging.Formatter('%(name)s: %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    return log

# City to well mapping
city_to_well = {
    "Barry": 61, "Belleville": 10, "Big Bend": 22, "Bondville": 1,
    "Boyleston": 221, "Brownstown": 3, "Cambridge": 51, "Carbondale": 11,
    "Crystal Lake": 41, "Dekalb": 5, "Dixon Springs": 2, "Fairfield": 34,
    "Fermi": 53, "Freeport": 13, "Galena": 21, "Good Hope": 72,
    "Greenfield": 132, "Janesville": 143, "Kilbourne": 7, "Monmouth": 6,
    "Mt. Morris": 31, "Olney": 12, "Peoria": 8, "Perry": 4,
    "Rend Lake": 14, "S.E. Illinois College": 202, "Snicarte": 91,
    "Sparta / Eden": 171, "Springfield": 9, "St. Charles": 20,
    "St. Peter": 153, "Stelle": 15, "SWS": 181
}

def get_groundwater_depth(city, month, year):
    log = configure_logging()
    headers = {'Referer': 'https://warm.isws.illinois.edu/warm/groundwater/'}
    url = f"https://warm.isws.illinois.edu/warm/groundwater/station.asp?well={city_to_well[city]}"

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        log.error(f"Failed to fetch the webpage. Status code: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    pattern = r"addRow\(\[new Date\((\d{4}) ,(\d{1,2}) ,(\d{1,2})\), (\d+\.\d+)\]\);"
    matches = re.findall(pattern, response.text)
    data = {(int(year), int(month) - 1): float(depth) for year, month, day, depth in matches}
    month_num = datetime.datetime.strptime(month, "%B").month - 1 if type(month) == str else month - 1

    depth = data.get((year, month_num))
    return depth

