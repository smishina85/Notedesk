import datetime
import logging


from apscheduler.schedulers.blocking import BlockingScheduler

from apscheduler.triggers.cron import CronTrigger

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
import django_apscheduler.jobstores

from django_apscheduler import util
from django_apscheduler.models import DjangoJobExecution

from notes.models import Category, Note

logger = logging.getLogger(__name__)


def my_job():
    date_wk_ago = datetime.datetime.today() - datetime.timedelta(days=7)
    notes = Note.objects.filter(time_in__gte=date_wk_ago)
    # need posts with assigned category (if post created from admin panel there couldn't be a category assigned
    # notes_categorized = notes.filter(post__isnull=False)

    if notes:  # if there is no any post for the last week no actions required
        # create a dictionary where key is a name of category and value is a list of emails of subscribers
        categories = list(Category.objects.all())

        for el in categories:
            cat_name = el.name_cat
            id_cat = el.id
            emails = list(set(list(User.objects.filter(subscriptions__category__exact=id_cat).values_list('email', flat=True))))
            if emails:
                subject = f'Notes published last week in category: {cat_name}'
                text_content = ''
                html_content = ''
                # print(cat_name)
                # need to have the list of id of last week posts assigned to exact category
                noteid_exact_cat = list(set(notes.filter(categ_id=id_cat).values_list('id', flat=True)))
                # print(noteid_exact_cat)

                for i in noteid_exact_cat:
                    note = Note.objects.get(pk=i)
                    text_var = note.title[:128]
                    pub_date = (note.time_in).date()
                    text_content += (f'{pub_date}  |  {text_var}  |   Ссылка на post: http://127.0.0.1:8000{note.get_absolute_url()}\n')
                    html_content += (f'{pub_date}  |  {text_var}  |  <br><a href="http://127.0.0.1:8000{note.get_absolute_url()}"></a>\n')
                # print(html_content)
                # print(emails)
                # print(text_content)

                for email in emails:
                    msg = EmailMultiAlternatives(subject, text_content, None, [email])
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()


# The `close_old_connections` decorator ensures that database connections,
# that have become unusable or are obsolete, are closed before and after your
# job has run. You should use it to wrap any jobs that you schedule that access
# the Django database in any way.

@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    """
        This job deletes APScheduler job execution entries older than `max_age`
        from the database.
        It helps to prevent the database from filling up with old historical
        records that are no longer useful.

        :param max_age: The maximum length of time to retain historical
                        job execution records. Defaults to 7 days.
        """
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(django_apscheduler.jobstores.DjangoJobStore(), "default")

        scheduler.add_job(
            my_job,
            trigger=CronTrigger('0 18 * * 4'),  # Every Friday at 18.00
            # trigger=CronTrigger(second="*/30"), # every 10 seconds
            id="my_job",  # The `id` assigned to each job MUST be unique
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added weekly job: 'delete_old_job_executions'.")

        try:
            logger.info("Starting scheduler ...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
