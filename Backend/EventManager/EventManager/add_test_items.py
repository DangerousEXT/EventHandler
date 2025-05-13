import os
import django
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EventManager.settings')
django.setup()

from app.models import Item

def add_test_items():
    items = [
        {
            'title': 'Event Hoodie',
            'description': 'A warm hoodie for event enthusiasts.',
            'price': 9000,
            'sponsor': 'sponsor2',
            'merch_type': 'hoodie',
        },
        {
            'title': 'Stylish Cap',
            'description': 'A cool cap for sunny events.',
            'price': 3000,
            'sponsor': 'sponsor1',
            'merch_type': 'cap',
        },
        {
            'title': 'Event Socks',
            'description': 'Comfortable socks with event branding.',
            'price': 1200,
            'sponsor': 'sponsor3',
            'merch_type': 'socks',
        },
        {
            'title': 'Event Sweatshirt',
            'description': 'A cozy sweatshirt for event lovers.',
            'price': 5200,
            'sponsor': 'sponsor1',
            'merch_type': 'sweatshirt',
        },
    ]

    for item_data in items:
        Item.objects.get_or_create(
            title=item_data['title'],
            defaults={
                'description': item_data['description'],
                'price': item_data['price'],
                'sponsor': item_data['sponsor'],
                'merch_type': item_data['merch_type'],
                'created_at': timezone.now(),
            }
        )
        print(f"Added item: {item_data['title']}")

if __name__ == "__main__":
    add_test_items()