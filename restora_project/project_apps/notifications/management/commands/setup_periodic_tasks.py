from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, CrontabSchedule

class Command(BaseCommand):
    help = 'Setup periodic tasks for Celery Beat'

    def handle(self, *args, **options):
        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute='0',
            hour='*/3', # 3 saatan bir yoxla 
            day_of_week='*',
            day_of_month='*',
            month_of_year='*',
            timezone='Asia/Baku'
        )
        PeriodicTask.objects.get_or_create(
            crontab=schedule,
            name='Check customer points daily',
            task='project_apps.notifications.tasks.check_customer_points',
        )
        self.stdout.write(self.style.SUCCESS('Periodic tasks setup successfully')) 