from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import register_events, DjangoJobStore

from mainapp.models import Review


def assignment_delete():
    Review.objects.all().update(first_assign_user=0)
    print('삭제완료')


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), 'djangojobstore')
    register_events(scheduler)

    @scheduler.scheduled_job('cron', hour='23', minute='59', name='assignment_delete')
    def auto_check():
        assignment_delete()

    scheduler.start()
