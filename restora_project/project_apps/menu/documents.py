from django_elasticsearch_dsl import Document, fields  # elastic search bar ucun documantasiya
from django_elasticsearch_dsl.registries import registry

from project_apps.menu.models import MenuItem

@registry.register_document
class MenuItemDocument(Document):
    name = fields.TextField(analyzer='standard')
    description = fields.TextField(analyzer='standard')
    category = fields.TextField(attr='category.name')
    price = fields.FloatField()
    discount_percentage = fields.IntegerField()
    is_available = fields.BooleanField()

    class Index:
        name = 'menu_items'
        settings = {'number_of_shards': 1, 'number_of_replicas': 1}

    class Django:
        model = MenuItem
        fields = []