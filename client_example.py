#!/usr/bin/env python3

import requests
import json

if __name__ == "__main__":
    url = "http://localhost:5000"
    data = {"id": "1337",
            "name": "example",
            "maintainer": "foo",
            "owner": "bar",
            "use_pol": "all",
            "discard_pol": "don't"}

    headers = {'Content-type': 'application/json',
               'Accept': 'text/plain'}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    if r.status_code == 200:
        print("OK")
    else:
        print("FAIL")
