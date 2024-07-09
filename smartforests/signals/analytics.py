from django.contrib.auth.signals import user_logged_in, user_logged_out
import wagtail.signals
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from wagtail.models import Revision
import posthog

from logbooks.models.pages import ContributorPage, ContributorsIndexPage


def identify_user(user):
    if user is None:
        return

    posthog.identify(
        user.id,
        {
            'email': user.email,
            'name': user.get_full_name()
        }
    )


@receiver(user_logged_in)
def login(sender, user, request, **kwargs):
    if user is None:
        return

    identify_user(user)
    posthog.capture(
        user.id,
        event='user login'
    )


@receiver(user_logged_out)
def logout(sender, user, request, **kwargs):
    if user is None:
        return

    identify_user(user)
    posthog.capture(
        user.id,
        event='user logout'
    )


@receiver(post_save, sender=User)
def create_user(sender, instance=None, created=False, **kwargs):
    if instance is None:
        return

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
    if user is None:
        return

    identify_user(user)
    posthog.capture(
        user.id,
        event='page published',
        properties={'id': instance.id,
                    'page': instance.title, 'pageType': instance.specific_class._meta.verbose_name}
    )


wagtail.signals.page_published.connect(page_published)


@receiver(post_save, sender=Revision)
def page_revision_created(sender, instance=None, created=False, **kwargs):
    if created:
        user = instance.user
        if user is None:
            return

        identify_user(user)
        posthog.capture(
            user.id,
            event='page revised',
            properties={'id': instance.content_object.id,
                        'page': instance.content_object.title,
                        'pageType': instance.content_object.specific_class._meta.verbose_name}
        )


def page_deleted(sender, instance, **kwargs):
    user = instance.owner
    if user is None:
        return

    identify_user(user)
    posthog.capture(
        user.id,
        event='page unpublished',
        properties={'id': instance.id,
                    'page': instance.title, 'pageType': sender._meta.verbose_name}
    )


wagtail.signals.page_unpublished.connect(page_deleted)


def workflow_submitted(sender, instance, user, **kwargs):
    if user is None:
        return

    page = instance.content_object

    if page is None:
        return

    identify_user(user)

    posthog.capture(
        user.id,
        event='workflow submitted',
        properties={'id': instance.id, 'workflow': instance.workflow.name,
                    'page': page.title,
                    'pageType': page._meta.verbose_name}
    )


wagtail.signals.workflow_submitted.connect(workflow_submitted)


def workflow_rejected(sender, instance, user, **kwargs):
    if user is None:
        return

    page = instance.content_object

    if page is None:
        return

    identify_user(user)

    posthog.capture(
        user.id,
        event='workflow rejected',
        properties={'id': instance.id, 'workflow': instance.workflow.name,
                    'page': page.title,
                    'pageType': page.specific_class._meta.verbose_name}
    )


wagtail.signals.workflow_rejected.connect(workflow_rejected)


def workflow_approved(sender, instance, user, **kwargs):
    if user is None:
        return

    page = instance.content_object

    if page is None:
        return

    identify_user(user)

    posthog.capture(
        user.id,
        event='workflow approved',
        properties={'id': instance.id, 'workflow': instance.workflow.name,
                    'page': page.title,
                    'pageType': page.specific_class._meta.verbose_name}
    )


wagtail.signals.workflow_approved.connect(workflow_approved)


def workflow_cancelled(sender, instance, user, **kwargs):
    identify_user(user)
    if user is None:
        return

    page = instance.content_object

    if page is None:
        return

    posthog.capture(
        user.id,
        event='workflow cancelled',
        properties={'id': instance.id, 'workflow': instance.workflow.name,
                    'page': page.title,
                    'pageType': page.specific_class._meta.verbose_name}
    )


wagtail.signals.workflow_cancelled.connect(workflow_cancelled)


def task_submitted(sender, instance, user, **kwargs):
    if user is None:
        return

    page = instance.revision.content_object if instance.revision else None

    if page is None:
        return

    posthog.capture(
        user.id,
        event='task submitted',
        properties={'id': instance.id, 'status': instance.status,
                    'task': instance.task.name, 'workflow': instance.workflow_state.workflow.name,
                    'page': page.title,
                    'pageType': page._meta.verbose_name}
    )


wagtail.signals.task_submitted.connect(task_submitted)


def task_rejected(sender, instance, user, **kwargs):
    if user is None:
        return

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


wagtail.signals.task_rejected.connect(task_rejected)


def task_approved(sender, instance, user, **kwargs):
    if user is None:
        return

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


wagtail.signals.task_approved.connect(task_approved)


def task_cancelled(sender, instance, user, **kwargs):
    if user is None:
        return

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


wagtail.signals.task_cancelled.connect(task_cancelled)
