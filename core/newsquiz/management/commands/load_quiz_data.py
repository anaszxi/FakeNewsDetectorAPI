from django.core.management.base import BaseCommand
from core.newsquiz.models import NewsQuizData
import pandas as pd
import os

class Command(BaseCommand):
    help = 'Loads quiz data from game_data.csv'

    def handle(self, *args, **kwargs):
        csv_path = r'C:\Users\TOSHIBA\PycharmProjects\Fake-News-Detector\app\FakeNewsDetectorAPI\game_data\game_data.csv'
        
        try:
            # Read the CSV file
            df = pd.read_csv(csv_path)
            self.stdout.write(f'Found {len(df)} rows in CSV file')
            
            # Create quiz questions from CSV data
            count = 0
            for _, row in df.iterrows():
                _, created = NewsQuizData.objects.get_or_create(
                    news_title=row['title'],
                    defaults={
                        'news_description': row['text'],
                        'label': row['label'] == 1  # Convert 1/0 to True/False
                    }
                )
                if created:
                    count += 1
            
            self.stdout.write(self.style.SUCCESS(f'Successfully loaded {count} new quiz questions'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error loading quiz data: {str(e)}')) 