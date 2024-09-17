from celery import shared_task


@shared_task
def sf_echo(msg):
    return msg
