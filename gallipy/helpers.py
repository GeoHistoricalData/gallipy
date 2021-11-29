import requests

def content_or_fail(response, f):
    if response.status_code != 200:
        response.raise_for_status()
    return f(response.content)

def sync_get(url, response_handler, qparams=None, headers=None):
    response = requests.get(url, params=qparams, headers=headers)
    return content_or_fail(response, response_handler)

