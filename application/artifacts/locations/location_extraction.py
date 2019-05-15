import os
import requests
from pprint import pprint
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from flask import current_app

from application.artifacts.locations.location import Location

class LocationExtractor:
    def __init__(self, artifact, file):
        self.artifact = artifact
        self.file = file

    def _load_image(self):
        self.image = Image.open(self.file)

    def _dms2dd(self, degrees, minutes, seconds, direction):
        dd = float(degrees) + float(minutes)/60 + float(seconds)/(60*60);
        if direction == 'S' or direction == 'W': dd *= -1
        return dd

    def _get_dd_coordinates(self, gps_info):
      latitude_dms = gps_info["GPSLatitude"]
      longitude_dms = gps_info["GPSLongitude"]

      latitude_dd = self._dms2dd(
        latitude_dms[0][0] / latitude_dms[0][1],
        latitude_dms[1][0] / latitude_dms[1][1],
        latitude_dms[2][0] / latitude_dms[2][1],
        gps_info["GPSLatitudeRef"],
      )

      longitude_dd = self._dms2dd(
        longitude_dms[0][0] / longitude_dms[0][1],
        longitude_dms[1][0] / longitude_dms[1][1],
        longitude_dms[2][0] / longitude_dms[2][1],
        gps_info["GPSLongitudeRef"],
      )

      return (latitude_dd, longitude_dd)

    def _extract_gps_coordinates(self):
        exif = self.image._getexif()
        gps_tag = 34853
        gps_info = {}

        for key in exif[gps_tag].keys():
            gps_info[GPSTAGS[key]] = exif[gps_tag][key]

        self.coordinates = self._get_dd_coordinates(gps_info)

    def _call_google_places_api(self):
        api_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        api_key = current_app.config["GOOGLE_MAPS_API_KEY"]

        params = {
          "key": api_key,
          "location": ','.join(map(str, self.coordinates)),
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
        self._load_image()
        self._extract_gps_coordinates()
        self._find_locations()
        self._save_locations_to_db()
