from apscheduler.schedulers.background import BackgroundScheduler

from .teams.placeholder_drives.drive import Drive


def add_background_jobs(app):
    sync_scheduler = BackgroundScheduler(deamon=False)

    def sync_with_context():
        with app.app_context():
            Drive.sync_all()

    sync_scheduler.add_job(sync_with_context, "interval", seconds=5)
    sync_scheduler.start()
    app.sync_scheduler = sync_scheduler
