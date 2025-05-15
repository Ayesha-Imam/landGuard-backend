import sys
import os
from apscheduler.schedulers.background import BackgroundScheduler
from .tasks import scheduled_post_to_facebook

scheduler = BackgroundScheduler()

def start():
    if 'runserver' not in sys.argv:
        return

    if os.environ.get('RUN_MAIN') != 'true':
        return

    if not scheduler.get_jobs():
        scheduler.add_job(
            scheduled_post_to_facebook,
            trigger='cron',
            day_of_week='mon',
            hour=9,
            minute=0,
            id='weekly_facebook_post'
        )
        scheduler.start()

