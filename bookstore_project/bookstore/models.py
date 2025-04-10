from django.db import models
from django.contrib.auth.models import User

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    publication_date = models.DateField(null=True, blank=True)
    # Add image field if needed: image = models.ImageField(upload_to='book_covers/', null=True, blank=True)

    def __str__(self):
        return self.title