from django.apps import AppConfig


class WagtailOverridesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'commonknowledge.wagtail_overrides'

    def ready(self):
        # Disable practically duplicate moderation notification
        # (the other one is 'group_approval_task_submitted_email_notification')
        from wagtail.models import WorkflowState
        from wagtail.signals import workflow_submitted
        workflow_submitted.disconnect(sender=WorkflowState, dispatch_uid="workflow_state_submitted_email_notification")