import requests
import json

starred_packages = set()

blacklist = {
    "thonny-circuitpython"
}

known_packages = set(starred_packages)

resp = requests.get("https://pypi.org/simple/", headers = {'Accept': 'application/vnd.pypi.simple.v1+json'})
assert resp.status_code == 200

projects = json.loads(resp.text)['projects']

for project in projects:
    name = project["name"]
    if "circuitpython" in name and name not in blacklist:
        known_packages.add(name)

print(f"Found {len(known_packages)} packages")

with open("known_packages_circuitpython_pypi.txt", "w", encoding="utf-8") as fp:
    for name in sorted(known_packages):
        ranking = 2 if name in starred_packages else 1
        fp.write(f"{name},{ranking}\n")


