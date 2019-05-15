from application.date.year import Year
from application.date.month import Month
from application.date.day import Day

class DateExtractor:
    def __init__(self, artifact, image):
        self.artifact = artifact
        self.image = image

    def _extract_date(self):
        if not hasattr(self.image, "_getexif"): return False

        exif = self.image._getexif()
        if not exif: return False

        datetime_tag = 0x9003
        if not datetime_tag in exif: return False

        self.date = exif[datetime_tag].rsplit(" ")[0]
        return True

    def _create_or_get_date(self, year, month, day):
        try:
            db_year = Year.nodes.get(value=year)
        except Year.DoesNotExist:
            db_year = Year(value=year)
            db_year.save()

        try:
            db_month = db_year.months.get(value=month)
        except Month.DoesNotExist:
            db_month = Month(value=month)
            db_month.save()
            db_month.year.connect(db_year)

        try:
            db_day = db_month.days.get(value=day)
        except Day.DoesNotExist:
            db_day = Day(value=day)
            db_day.save()
            db_day.month.connect(db_month)

        return db_day

    def _save_date_to_db(self):
        year, month, day = self.date.rsplit(":")
        db_day = self._create_or_get_date(year, month, day)
        self.artifact.day.connect(db_day)

    def run(self):
        if not self._extract_date(): return
        self._save_date_to_db()
