from django.db import models
from django.utils import timezone

class URL(models.Model):
    init_url = models.CharField(max_length=1000)
    final_url = models.CharField(max_length=1000)
    status = models.CharField(max_length=4)
    title = models.CharField(max_length=500)
    collected_date = models.DateTimeField(default=timezone.now)
    wback_url = models.URLField(max_length=1000, default='')
    wback_date = models.DateTimeField(default=timezone.now)

    def collect(self):
        self.save()

    def __str__(self):
        return self.init_url