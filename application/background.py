from apscheduler.schedulers.background import BackgroundScheduler

from .teams.placeholder_drives.drive import Drive


def add_background_jobs(app):
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(Drive.sync_all, 'interval', minutes=5)
    sched.start()

