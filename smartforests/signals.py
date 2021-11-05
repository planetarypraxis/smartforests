from django.contrib.auth.signals import user_logged_in, user_logged_out
import wagtail.core.signals
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from wagtail.core.models import Page, PageRevision
import posthog

from logbooks.models.pages import ContributorPage, ContributorsIndexPage


def identify_user(user):
    posthog.identify(
        user.id,
        {
            'email': user.email,
            'name': user.get_full_name()
        }
    )


@receiver(user_logged_in)
def login(sender, user, request, **kwargs):
    identify_user(user)
    posthog.capture(
        user.id,
        event='user login'
    )


@receiver(user_logged_out)
def logout(sender, user, request, **kwargs):
    identify_user(user)
    posthog.capture(
        user.id,
        event='user logout'
    )


@receiver(post_save, sender=User)
def create_user(sender, instance=None, created=False, **kwargs):
    if created:
        user = instance
        identify_user(user)
        posthog.capture(
            user.id,
            event='user registered'
        )

        ContributorPage.create_for_user(user)


def page_published(sender, instance, **kwargs):
    user = instance.owner
    identify_user(user)
    posthog.capture(
        user.id,
        event='page published',
        properties={'id': instance.id,
                    'page': instance.title, 'pageType': instance.specific_class._meta.verbose_name}
    )


wagtail.core.signals.page_published.connect(page_published)


@receiver(post_save, sender=PageRevision)
def page_revision_created(sender, instance=None, created=False, **kwargs):
    if created:
        user = instance.user
        identify_user(user)
        posthog.capture(
            user.id,
            event='page revised',
            properties={'id': instance.page.id,
                        'page': instance.page.title,
                        'pageType': instance.page.specific_class._meta.verbose_name}
        )


def page_deleted(sender, instance, **kwargs):
    user = instance.owner
    identify_user(user)
    posthog.capture(
        user.id,
        event='page unpublished',
        properties={'id': instance.id,
                    'page': instance.title, 'pageType': sender._meta.verbose_name}
    )


wagtail.core.signals.page_unpublished.connect(page_deleted)


def workflow_submitted(sender, instance, user, **kwargs):
    identify_user(user)
    posthog.capture(
        user.id,
        event='workflow submitted',
        properties={'id': instance.id, 'workflow': instance.workflow.name,
                    'page': instance.page.title,
                    'pageType': instance.page.specific_class._meta.verbose_name}
    )


wagtail.core.signals.workflow_submitted.connect(workflow_submitted)


def workflow_rejected(sender, instance, user, **kwargs):
    identify_user(user)
    posthog.capture(
        user.id,
        event='workflow rejected',
        properties={'id': instance.id, 'workflow': instance.workflow.name,
                    'page': instance.page.title,
                    'pageType': instance.page.specific_class._meta.verbose_name}
    )


wagtail.core.signals.workflow_rejected.connect(workflow_rejected)


def workflow_approved(sender, instance, user, **kwargs):
    identify_user(user)
    posthog.capture(
        user.id,
        event='workflow approved',
        properties={'id': instance.id, 'workflow': instance.workflow.name,
                    'page': instance.page.title,
                    'pageType': instance.page.specific_class._meta.verbose_name}
    )


wagtail.core.signals.workflow_approved.connect(workflow_approved)


def workflow_cancelled(sender, instance, user, **kwargs):
    identify_user(user)
    posthog.capture(
        user.id,
        event='workflow cancelled',
        properties={'id': instance.id, 'workflow': instance.workflow.name,
                    'page': instance.page.title,
                    'pageType': instance.page.specific_class._meta.verbose_name}
    )


wagtail.core.signals.workflow_cancelled.connect(workflow_cancelled)


def task_submitted(sender, instance, user, **kwargs):
    page = instance.workflow_state.page
    identify_user(user)
    posthog.capture(
        user.id,
        event='task submitted',
        properties={'id': instance.id, 'status': instance.status,
                    'task': instance.task.name, 'workflow': instance.workflow_state.workflow.name,
                    'page': page.title,
                    'pageType': page.specific_class._meta.verbose_name}
    )


wagtail.core.signals.task_submitted.connect(task_submitted)


def task_rejected(sender, instance, user, **kwargs):
    page = instance.workflow_state.page
    identify_user(user)
    posthog.capture(
        user.id,
        event='task rejected',
        properties={'id': instance.id, 'status': instance.status,
                    'task': instance.task.name, 'workflow': instance.workflow_state.workflow.name,
                    'page': page.title,
                    'pageType': page.specific_class._meta.verbose_name}
    )


wagtail.core.signals.task_rejected.connect(task_rejected)


def task_approved(sender, instance, user, **kwargs):
    page = instance.workflow_state.page
    identify_user(user)
    posthog.capture(
        user.id,
        event='task approved',
        properties={'id': instance.id, 'status': instance.status,
                    'task': instance.task.name, 'workflow': instance.workflow_state.workflow.name,
                    'page': page.title,
                    'pageType': page.specific_class._meta.verbose_name}
    )


wagtail.core.signals.task_approved.connect(task_approved)


def task_cancelled(sender, instance, user, **kwargs):
    page = instance.workflow_state.page
    identify_user(user)
    posthog.capture(
        user.id,
        event='task cancelled',
        properties={'id': instance.id, 'status': instance.status,
                    'task': instance.task.name, 'workflow': instance.workflow_state.workflow.name,
                    'page': page.title,
                    'pageType': page.specific_class._meta.verbose_name}
    )


wagtail.core.signals.task_cancelled.connect(task_cancelled)
