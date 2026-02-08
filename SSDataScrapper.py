import requests
import json


API_URL = "https://api.le-systeme-solaire.net/rest/bodies"
API_KEY = "b1bf9397-9cf1-4f5b-955e-e063b5e06cc3"       
OUTPUT_FILE = "solarsystem.txt"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json"
}

response = requests.get(API_URL, headers=headers, timeout=30)
response.raise_for_status()

data = response.json()
bodies = data.get("bodies", [])

print(f"Fetched {len(bodies)} celestial bodies")


with open(OUTPUT_FILE, "w", encoding="utf-8") as f:

    for body in bodies:
        f.write("====================================\n")
        f.write(f"Name: {body.get('englishName', 'Unknown')}\n")
        f.write(f"Type: {body.get('bodyType', 'Unknown')}\n")

        if body.get("isPlanet"):
            f.write("This body is a planet.\n")

        if body.get("aroundPlanet"):
            planet = body["aroundPlanet"].get("planet")
            if planet:
                f.write(f"Orbits planet: {planet}\n")

        if body.get("meanRadius"):
            f.write(f"Mean Radius: {body['meanRadius']} km\n")

        if body.get("gravity"):
            f.write(f"Gravity: {body['gravity']} m/s²\n")

        if body.get("density"):
            f.write(f"Density: {body['density']} g/cm³\n")

        if body.get("escape"):
            f.write(f"Escape Velocity: {body['escape']} m/s\n")

        if body.get("sideralOrbit"):
            f.write(f"Orbital Period: {body['sideralOrbit']} days\n")

        if body.get("mass"):
            m = body["mass"]
            f.write(
                f"Mass: {m['massValue']} × 10^{m['massExponent']} kg\n"
            )

        if body.get("discoveredBy"):
            f.write(f"Discovered By: {body['discoveredBy']}\n")

        f.write("\n")

print(f"Data saved successfully to {OUTPUT_FILE}")
