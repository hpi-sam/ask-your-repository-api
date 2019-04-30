from apscheduler.schedulers.background import BackgroundScheduler

from .teams.placeholder_drives.drive import Drive


def add_background_jobs(app):
    sched = BackgroundScheduler(deamon=False)

    def sync_with_context():
        with app.app_context():
            Drive.sync_all()

    sched.add_job(sync_with_context, "interval", seconds=30)
    sched.start()
