import urllib.request
page = urllib.request.urlopen('https://warm.isws.illinois.edu/warm/soil/')
print(page.read())