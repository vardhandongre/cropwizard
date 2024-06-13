# python script to send a GET request to default.aspx url endpoint and get the response
import requests
from bs4 import BeautifulSoup
# import json
# import sys
# import os
# import time
# import datetime
# import re


# # set up url 
# url = https://warm.isws.illinois.edu/warm/stationmeta.asp?import requests

url = "https://warm.isws.illinois.edu/warm/soil/"
# params = {
#     "site": "BVL",
#     "from": "sl"
# }

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Sec-Ch-Ua": "\"Chromium\";v=\"124\", \"Google Chrome\";v=\"124\", \"Not-A.Brand\";v=\"99\"",
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "\"macOS\"",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1"
}

def get_params(station):
    station2site = {
        "Belleville":'FRM',
        "Big Bend":'BBC',
        "Bondville":'BVL',
        "Brownstown":'BRW',
        "Carbondale":'SIU',
        "Champaign":'CMI',
        "DeKalb":'DEK',
        "Dixon Spring":'DXS',
        "Fairfield":'FAI',
        "Freeport":'FRE',
        "Monmouth":'MON',
        "Olney":'OLN',
        "Peoria":'ICC',
        "Perry":'ORR',
        "Rend Lake":'RND',
        "Snicarte":'SNI',
        "Springfield":'LLC',
        "Stelle":'STE',
        "St. Charles":'STC'
    }
    return station2site[station]

# Parse the response
def parse_response(html_response):
    soup = BeautifulSoup(html_response, 'html.parser')

    def get_value(label):
        element = soup.find(string=label)
        if element and element.parent:
            return element.parent.text.split(":")[1].strip()
        return None

    conditions = {
        "As of": get_value("As of"),
        "Air Temperature": get_value("Air Temperature:"),
        "Dew Point": get_value("Dew Point:"),
        "Relative Humidity": get_value("Relative Humidity:"),
        "Barometric Pressure (sea level)": get_value("Barometric Press. (sea level):"),
        "Wind Speed": get_value("Wind Speed:"),
        "Wind Direction": get_value("Wind Direction:"),
        "Precipitation": get_value("Precipitation:"),
        "Soil Temp 2\" (Bare Soil)": get_value('Soil Temp 2" (Bare Soil):'),
        "Soil Temp 4\" (Bare Soil)": get_value('Soil Temp 4" (Bare Soil):'),
        "Soil Temp 4\" (Sod)": get_value('Soil Temp 4" (Sod):'),
        "Soil Temp 8\" (Sod)": get_value('Soil Temp 8" (Sod):')
    }

    return conditions

def main():
    station = input("Enter the station name: ")
    params = get_params(station)
    payload = {
    "site": params,
    "from": "sl"
}
    response = response = requests.post(url, headers=headers, data=payload)
    # Print the response text to see the result
    print(response.text)
    conditions = parse_response(response.text)
    print(conditions)

if __name__ == "__main__":
    main()