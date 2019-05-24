import requests
from flask import current_app

from application.artifacts.locations.location import Location

class LocationDetermination:
    def __init__(self, artifact):
        self.artifact = artifact

    def _call_google_places_api(self):
        api_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        api_key = current_app.config["GOOGLE_MAPS_API_KEY"]

        params = {
          "key": api_key,
          "location": ','.join(map(str, self.artifact.coordinates)),
          "radius": 50,
        }

        headers = {"Content-Type": "application/json"}
        response = requests.request("GET", api_url, headers=headers, params=params)
        return response.json()

    def _find_locations(self):
        response = self._call_google_places_api()
        self.locations = response["results"]

    def _save_locations_to_db(self):
        for location in self.locations:
            db_location = Location(name=location["name"])
            db_location.save()
            db_location.artifact.connect(self.artifact)

    def run(self):
        if not self.artifact.coordinates: return
        self._find_locations()
        self._save_locations_to_db()
