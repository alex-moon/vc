import dotenv
import requests
import shutil
from datetime import datetime

print("Running latest %s" % datetime.now())

response = requests.get(
    'https://vc-api.ajmoon.uk/api/generation-request/',
    headers={
        "Authorization": "Bearer %s" % dotenv.get_key('.env', 'APP_KEY')
    }
)
if response.status_code == 200:
    print('- got latest, replacing latest.json')
    # print(response.text);exit()
    with open('/opt/vc/app/assets/latest.json', 'w') as outfile:
        outfile.write(response.text)
