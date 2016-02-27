import json
import urllib.request

def mod_vpl_info(url):
    req = urllib.request.Request(url + 'mod_vpl_info')
    try:
        with urllib.request.urlopen(req) as response:
            page = response.read()
    except:
        return None

    page = page.decode('utf-8')
    return json.loads(page)
