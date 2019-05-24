from PIL.ExifTags import TAGS, GPSTAGS

from application.artifacts.locations.location import Location

class CoordinatesExtractor:
    def __init__(self, artifact, image):
        self.artifact = artifact
        self.image = image

    def _dms2dd(self, degrees, minutes, seconds, direction):
        dd = float(degrees) + float(minutes) / 60 + float(seconds) / (60 * 60)
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

    def _check_for_gps_data(self):
        if not hasattr(self.image, "_getexif"): return False

        exif = self.image._getexif()
        if not exif: return False

        gps_tag = 34853
        if not gps_tag in exif: return False

        gps_info = {}

        for key in exif[gps_tag].keys():
            gps_info[GPSTAGS[key]] = exif[gps_tag][key]

        for prop in ["GPSLatitude", "GPSLongitude", "GPSLatitudeRef", "GPSLongitudeRef"]:
            if not prop in gps_info: return False

        self.gps_info = gps_info
        return True

    def _extract_gps_coordinates(self):
        self.coordinates = self._get_dd_coordinates(self.gps_info)

    def _save_coordinates_to_db(self):
        self.artifact.update(coordinates=self.coordinates)

    def run(self):
        if not self._check_for_gps_data(): return
        self._extract_gps_coordinates()
        self._save_coordinates_to_db()
