from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import register_events, DjangoJobStore

from . import models as main_models


# 할당 상태 자동 리셋
def assignment_delete():
    main_models.Review.objects.all().update(assigned_user=None)
    print("할당 상태 자동 리셋 완료")


# 오후 23시 59분마다 리셋됨
def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "djangojobstore")
    register_events(scheduler)

    @scheduler.scheduled_job("cron", hour="23", minute="59", name="assignment_delete")
    def auto_check():
        assignment_delete()

    scheduler.start()
