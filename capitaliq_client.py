import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()

api_token_url = "https://api-ciq.marketintelligence.spglobal.com/gdsapi/rest/authenticate/api/v1/token"

headers = {
    "Accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded",
}
data = {
    "username": os.getenv("CAPITALIQ_USER"),
    "password": os.getenv("CAPITALIQ_PASS")
}

session = requests.Session()
response = session.post(api_token_url, headers=headers, data=data)

if response.status_code == 200:
    response_data = response.json()
    access_token = response_data.get("access_token")
    print("Status Code: ", response.status_code)
else:
    print(f"Failed to receive token: {response.status_code} - {response.text}")

endpoint_url =  "https://api-ciq.marketintelligence.spglobal.com/gdsapi/rest/v3/clientservice.json"

bearer_token = access_token
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {bearer_token}"
}

req_array = [
{"function": "GDSHE", "identifier": "IBM:NYSE", "mnemonic": "IQ_EBITDA", "properties":
{"PeriodType": "IQ_FY-4", "restatementTypeId": "LC"}},
]
payload = {"inputRequests": req_array}

capiqResponse = requests.post(
    endpoint_url,
    headers=headers,
    data=json.dumps(payload)
)
capiqResponse.raise_for_status()
response_data = capiqResponse.json()
print(response_data)