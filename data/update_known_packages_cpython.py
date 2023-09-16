import requests
import json

starred_packages = {
    "easygui",
    "matplotlib",
    "numpy",
    "pandas",
    "pygame",
    "requests",
}

known_packages = set(starred_packages)

resp = requests.get("https://hugovk.github.io/top-pypi-packages/top-pypi-packages-30-days.min.json")
assert resp.status_code == 200

input_rows = json.loads(resp.text)["rows"]
for row in input_rows:
    known_packages.add(row["project"])

print(f"Found {len(known_packages)} packages")

with open("known_packages_cpython_pypi.txt", "w", encoding="utf-8") as fp:
    for name in sorted(known_packages):
        ranking = 2 if name in starred_packages else 1
        fp.write(f"{name},{ranking}\n")


