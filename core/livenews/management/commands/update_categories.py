from django.core.management.base import BaseCommand
from core.livenews.models import NewsCategory

class Command(BaseCommand):
    help = 'Update news categories to match The Guardian sections'

    def handle(self, *args, **kwargs):
        # The Guardian's main sections matching the original version
        guardian_sections = [
            'sport',
            'world',
            'society',
            'books',
            'lifeandstyle',  # Life and Style
            'artanddesign',  # Art and Design
            'us-news',       # US News
            'commentisfree', # Comment is Free
            'fashion',
            'news',
            'education',
            'politics',
            'tv-and-radio',  # TV and Radio
            'business',
            'uk-news',       # UK News
            'environment',
            'football'
        ]

        # Deactivate all existing categories
        NewsCategory.objects.all().update(is_active=False)

        # Create or update categories
        for section in guardian_sections:
            category, created = NewsCategory.objects.get_or_create(
                name=section,
                defaults={'is_active': True}
            )
            if not created:
                category.is_active = True
                category.save()
            
            action = 'Created' if created else 'Updated'
            self.stdout.write(f"{action} category: {section}")

        self.stdout.write(self.style.SUCCESS(f'Successfully updated {len(guardian_sections)} categories')) 