from django.db import models
from django.core.validators import MinLengthValidator
from django.utils import timezone


class LiveNews(models.Model):
    """Model to store news from Guardian API with predictions."""
    title = models.CharField(max_length=2000, validators=[MinLengthValidator(10)])
    publication_date = models.DateTimeField()
    news_category = models.CharField(max_length=200)
    prediction = models.BooleanField(default=True)
    confidence = models.FloatField(default=0.84)
    section_id = models.CharField(max_length=200)
    section_name = models.CharField(max_length=200)
    type = models.CharField(max_length=200, choices=[
        ('article', 'Article'),
        ('liveblog', 'Live Blog'),
        ('video', 'Video')
    ])
    web_url = models.URLField(max_length=600, unique=True)
    img_url = models.URLField(max_length=600, blank=True)

    class Meta:
        ordering = ['-publication_date']
        indexes = [
            models.Index(fields=['news_category']),
            models.Index(fields=['publication_date']),
            models.Index(fields=['web_url'])
        ]
        verbose_name = 'Live News'
        verbose_name_plural = 'Live News'

    def __str__(self):
        return self.title

    @property
    def reliability_score(self):
        """Return the reliability score as a percentage."""
        return int(self.confidence * 100)

    def save(self, *args, **kwargs):
        """Override save to ensure publication_date is timezone-aware."""
        if self.publication_date and timezone.is_naive(self.publication_date):
            self.publication_date = timezone.make_aware(self.publication_date)
        super().save(*args, **kwargs)


class NewsCategory(models.Model):
    """Model to store news categories and their latest fetch times."""
    name = models.CharField(max_length=200, unique=True)
    last_fetch = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "News Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def update_last_fetch(self):
        """Update the last fetch time to now."""
        self.last_fetch = timezone.now()
        self.save()
