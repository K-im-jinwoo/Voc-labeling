# import schedule
# import time
# from django.core.management.base import BaseCommand
# from main import models as main_models


# class Command(BaseCommand):
#     help = '매일 자정 리뷰의 사용자 할당 상태 초기화'

#     def handle(self, *args, **kwargs):
#         self.reset_assigned()

#         # 스케줄러 설정
#         # schedule.every(1).seconds.do(self.reset_assigned)
#         schedule.every().day.at("00:00:00").do(self.reset_assigned)

#         # 무한 루프를 사용하여 스케줄러를 주기적으로 실행
#         while True:
#             schedule.run_pending()
#             time.sleep(1)

#     def reset_assigned(self):
#         main_models.Review.objects.all().update(assigned_user=None)

# from django.core.management.base import BaseCommand
# from apscheduler.schedulers.background import BackgroundScheduler
# from main import models as main_models

# class Command(BaseCommand):
#     help = '매일 자정 리뷰의 사용자 할당 상태 초기화'

#     def handle(self, *args, **kwargs):
#         scheduler = BackgroundScheduler()
#         scheduler.add_job(self.reset_assigned, 'cron', hour=0, minute=0)  # 매일 자정에 실행
#         scheduler.start()

#         try:
#             self.stdout.write(self.style.SUCCESS('Scheduler started'))
#             while True:
#                 pass
#         except KeyboardInterrupt:
#             scheduler.shutdown()
#             self.stdout.write(self.style.SUCCESS('Scheduler stopped'))

#     def reset_assigned(self):
#         main_models.Review.objects.all().update(assigned_user=None)

from django.core.management.base import BaseCommand
from apscheduler.schedulers.background import BackgroundScheduler
from main import models as main_models
import logging
from datetime import datetime

class Command(BaseCommand):
    help = '매일 자정 리뷰의 사용자 할당 상태 초기화'

    def __init__(self):
        super(Command, self).__init__()

        # 로그 설정
        logging.basicConfig(filename='scheduler.log', level=logging.INFO, format='%(asctime)s - %(message)s')

    def handle(self, *args, **kwargs):
        scheduler = BackgroundScheduler()
        scheduler.add_job(self.reset_assigned, 'cron', hour=0, minute=0)
        scheduler.start()

        try:
            self.stdout.write(self.style.SUCCESS('Scheduler started'))
            while True:
                pass
        except KeyboardInterrupt:
            scheduler.shutdown()
            self.stdout.write(self.style.SUCCESS('Scheduler stopped'))

    def reset_assigned(self):
        main_models.Review.objects.all().update(assigned_user=None)

        # 로그 남기기
        current_time = datetime.now().strftime('%Y.%m.%d %H:%M:%S')
        log_message = f'{current_time}: Reset the user assignment status of the review.'
        logging.info(log_message)