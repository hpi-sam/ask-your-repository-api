from apscheduler.schedulers.background import BackgroundScheduler

from .teams.drives.drive import Drive
from .artifacts.faces.face_recognition import FaceRecognition
from .artifacts.image_recognition import ImageRecognizer
from .artifacts.locations.location_determination import LocationDeterminator

def add_drive_sync_job(app):
    sync_scheduler = BackgroundScheduler(deamon=False, timezone="Europe/Berlin")

    for drive in Drive.all():
        drive.update(is_syncing=False)

    def sync_with_context():
        with app.app_context():
            print("syncing drives")  # noqa
            Drive.sync_all()
            print("done")  # noqa

    sync_scheduler.add_job(sync_with_context, "interval", seconds=600)
    if app.config["START_DRIVE_SYNC_WORKER"]:
        sync_scheduler.start()
    app.sync_scheduler = sync_scheduler

def add_image_recognition_job(app):
    scheduler = BackgroundScheduler(deamon=False, timezone="Europe/Berlin")

    def run_with_context():
        with app.app_context():
            ImageRecognizer.run()

    scheduler.add_job(run_with_context, "interval", seconds=5)
    scheduler.start()

def add_face_recognition_job(app):
    scheduler = BackgroundScheduler(deamon=False, timezone="Europe/Berlin")

    def run_with_context():
        with app.app_context():
            FaceRecognition.run()

    scheduler.add_job(run_with_context, "interval", seconds=5)
    scheduler.start()

def add_location_determination_job(app):
    scheduler = BackgroundScheduler(deamon=False, timezone="Europe/Berlin")

    def run_with_context():
        with app.app_context():
            LocationDeterminator.run()

    scheduler.add_job(run_with_context, "interval", seconds=5)
    scheduler.start()

def add_background_jobs(app):
    add_drive_sync_job(app)
    add_face_recognition_job(app)
    add_image_recognition_job(app)
