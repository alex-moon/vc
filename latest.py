from datetime import datetime

import requests

print("Running latest %s" % datetime.now())

response = requests.get('https://vc-api.ajmoon.uk/api/generation-request/')
if response.status_code == 200:
    print('- got latest, replacing latest.json')
    with open('/opt/vc/public/assets/latest.json', 'w') as outfile:
        outfile.write(response.text)
