from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from project_apps.notifications.models import Notification

@registry.register_document
class NotificationDocument(Document):
    user_email = fields.TextField(attr='user.email')
    title = fields.TextField(analyzer='standard')
    message = fields.TextField(analyzer='standard')
    is_read = fields.BooleanField()
    sent_at = fields.DateField()

    class Index:
        name = 'notifications'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 1
        }

    class Django:
        model = Notification
        fields = []