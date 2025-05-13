# import sys
# from apscheduler.schedulers.background import BackgroundScheduler
# from .tasks import scheduled_post_to_facebook

# scheduler = BackgroundScheduler()

# def start():
#     # Only run scheduler when using the development server
#     if 'runserver' not in sys.argv:
#         return
    
#     if not scheduler.get_jobs():  # Avoid re-adding if already running
#         scheduler.add_job(
#             scheduled_post_to_facebook,
#             'cron',
#             day_of_week='mon',  # every Monday
#             hour=10,            # at 10 AM
#             minute=0,
#             id='weekly_facebook_post'
#         )
#         scheduler.start()


import sys
import os
from apscheduler.schedulers.background import BackgroundScheduler
from .tasks import scheduled_post_to_facebook

scheduler = BackgroundScheduler()

def start():
    if 'runserver' not in sys.argv:
        return

    # Only run in the main thread, not the reloader
    if os.environ.get('RUN_MAIN') != 'true':
        return

    if not scheduler.get_jobs():
        scheduler.add_job(
            trigger='cron',
            day_of_week='mon',  
            hour=9,              
            minute=0,
            id='weekly_facebook_post'
        )
        scheduler.start()
