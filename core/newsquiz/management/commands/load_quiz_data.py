from django.core.management.base import BaseCommand
from core.newsquiz.models import NewsQuizData
import pandas as pd
import os
from pathlib import Path

class Command(BaseCommand):
    help = 'Loads quiz data from game_data.csv'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv-file',
            type=str,
            help='Optional: Path to the CSV file. If not provided, will use default game_data.csv',
            required=False
        )

    def handle(self, *args, **options):
        # Get the base directory of the project
        base_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
        
        # Use provided CSV path or default to game_data/game_data.csv
        if options.get('csv_file'):
            csv_path = options['csv_file']
        else:
            csv_path = os.path.join(base_dir, 'game_data', 'game_data.csv')
        
        try:
            # Verify file exists
            if not os.path.exists(csv_path):
                raise FileNotFoundError(f'CSV file not found at: {csv_path}')

            # Read the CSV file
            df = pd.read_csv(csv_path)
            self.stdout.write(f'Found {len(df)} rows in CSV file')
            
            # Create quiz questions from CSV data
            count = 0
            for _, row in df.iterrows():
                try:
                    _, created = NewsQuizData.objects.get_or_create(
                        news_title=row['title'],
                        defaults={
                            'news_description': row['text'],
                            'label': bool(row['label'])  # Convert to boolean
                        }
                    )
                    if created:
                        count += 1
                except Exception as row_error:
                    self.stdout.write(
                        self.style.WARNING(f'Error processing row: {row["title"][:50]}... - {str(row_error)}')
                    )
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully loaded {count} new quiz questions')
            )
            
        except pd.errors.EmptyDataError:
            self.stdout.write(
                self.style.ERROR('The CSV file is empty')
            )
        except pd.errors.ParserError:
            self.stdout.write(
                self.style.ERROR('Error parsing CSV file - make sure it is properly formatted')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error loading quiz data: {str(e)}')
            )