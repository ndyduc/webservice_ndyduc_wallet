
import json
import requests
import urllib.parse
import hashlib
import hmac
import base64
import time
import requests
from django.http import JsonResponse


def kraken_api(request):
    # Code to send request to Kraken
    kraken_response = requests.get('https://api.kraken.com/0/public/Ticker?pair=XBTUSD')

    # Check if the request was successful
    if kraken_response.status_code == 200:
        # Parse the response JSON
        kraken_data = kraken_response.json()

        # Return the Kraken data as JSON response
        return JsonResponse(kraken_data)
    else:
        # Return an error response if the request was not successful
        return JsonResponse({'error': 'Failed to fetch data from Kraken'}, status=kraken_response.status_code)



# django-admin startproject ndyduc 
# python3 manage.py migrate
# python3 manage.py runserver

def call_api(token):
    url = 'https://api.kraken.com/0/public/Ticker?pair='+token
    # url = "wss://demo-futures.kraken.com/ws/v1"
    
    try:
        response = requests.get(url)  # Gửi yêu cầu GET đến API
        response.raise_for_status()  # Ném một ngoại lệ nếu có lỗi trong phản hồi

        json_data = response.json()  # Lấy dữ liệu JSON từ phản hồi
        return json_data
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return None

# print(call_api("XETHZUSD"))
# print(json.dumps((getticker(call_api(), "XETHZUSD")).__dict__))

# print(json.dumps(call_api())) 


api_url = "https://futures.kraken.com"
api_key = 'nlvZERtzDr5sWu4wQeMOyeZQq+YCZ0WFOPsDlaeLaNvN5kPoH7wNd36s'
api_sec = 'LoJsSETsagjpYNGKBXTlSamFISTDE7nDD99Fdz7rG5ENJ/dmGooc0NyEYbedNHazuBcZQkMZHNN6JL5ooTJNaLD3'

read_key = 'J8KTagQmyNMmvT4WxvPfrvoQHb94cI+vJ/NIMGYf74+DbwNeLBv35163'
read_sec = 'XE6IUF8kyo3mXf5QYaIaMoR1MIpNyIZEQwMqVRH4rSFkVFtSDNKmaqn9hFurmAAMDEGU7fX28/MueGOKGX4Q5hPx'

demo_apikey = 'D8d22EHn6x7iDUtZ++cF95PUNnblxsN3jQct2/+0lELlV+9lkjk0id4N'
demo_apisec = 'JPisYm9qvwvgvPjx1vvrvYYAVj+B2KGAqXRMDLUXrX3muoYu9YHu2/qikgj4f1QOGjo2ImMOueF/FBXGdr8ht+tj'


def get_kraken_signature(urlpath, data, secret):
    postdata = urllib.parse.urlencode(data)
    encoded = (str(data['nonce']) + postdata).encode()
    message = urlpath.encode() + hashlib.sha256(encoded).digest()

    mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
    sigdigest = base64.b64encode(mac.digest())
    return sigdigest.decode()
# print("API-Sign: {}".format(get_kraken_signature("/0/private/AddOrder", data, api_sec)))


# Attaches auth headers and returns results of a POST request
def kraken_request(uri_path, data, api_key, api_sec):
    headers = {}
    headers['API-Key'] = api_key
    headers['API-Sign'] = get_kraken_signature(uri_path, data, api_sec)             
    req = requests.post((api_url + uri_path), headers=headers, data=data)
    return req

# Construct the request and print the result as text
resp = kraken_request('/0/private/Balance', {
    "nonce": str(int(1000*time.time()))
}, api_key, api_sec)

# print(resp.text)

