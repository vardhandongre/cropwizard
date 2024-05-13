# create API endpoints using Flask
# create a POST endpoint for GDD calculation
# create a POST endpoint for PDD calculation
# create a POST endpoint for seasonal maps
# create a POST endpoint for groundwater data

from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

@app.route('/gdd', methods=['POST'])
