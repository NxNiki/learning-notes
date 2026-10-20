# set up account for yelp api before running this.

import requests
url = "https://api.yelp.com/v3/businesses/search"
api_key = "" # set the api key on yelp api
headers = {
  "Authorization": "Bearer " + api_key
}
params = {
  # "term": "Barber", 
  "loacation": "NYC"
}

response = requests.get(url, headers=headers, params=params)
print(response.text)
print(response.json())

businesses = response.json()["businesses"]

for business in businesses:
  print(business["name"])

names = [business["name"] for business in businesses if business["rating"] > 4.5]

# hiding API keys:
## put api key in a file config.py and remove it from git hub.
import config

headers = {
  "Authorization": "Bearer " + config.api_key
}


