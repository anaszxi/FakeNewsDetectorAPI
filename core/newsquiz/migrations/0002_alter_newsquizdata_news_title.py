# Generated by Django 4.2.3 on 2024-12-05 08:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core_newsquiz', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newsquizdata',
            name='news_title',
            field=models.CharField(max_length=2000),
        ),
    ]
