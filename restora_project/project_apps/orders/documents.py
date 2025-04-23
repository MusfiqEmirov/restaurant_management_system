from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from project_apps.orders.models import Order


@registry.register_document
class OrderDocument(Document):
    user_email = fields.TextField(attr='user.email')
    total_amount = fields.FloatField()
    status = fields.TextField()

    class Index:
        name = 'orders'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 1
        }

    class Django:
        model = Order
        fields = []