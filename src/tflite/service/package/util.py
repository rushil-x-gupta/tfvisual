#
# util.py
#
# Sanjeev Gupta, April 2020

import requests

def inference_publish(url, inference_data_json):
    req = {}
    try:
        header = {"Content-type": "application/json", "Accept": "text/plain"} 
        req = requests.post(url, data=inference_data_json, headers=header)
    except:
        print ()

    return ""
