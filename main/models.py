from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import os
from datetime import datetime

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    can_view = models.BooleanField(default=False)
    can_upload = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

class ExcelFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='excel_files/')
    file_name = models.CharField(max_length=255)
    upload_date = models.DateTimeField(auto_now_add=True)
    has_header = models.BooleanField(default=True)
    file_size = models.IntegerField(default=0)  # Size in bytes
    
    # New fields for financial year and client information
    financial_year = models.CharField(max_length=9, default='2024-2025')  # Format: 2023-2024
    client_po_number = models.CharField(max_length=100, blank=True, null=True)
    client_po_date = models.DateField(blank=True, null=True)
    sales_document = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        ordering = ['-upload_date']
        unique_together = ['client_po_number', 'client_po_date', 'sales_document']

    def save(self, *args, **kwargs):
        if not self.file_name and self.file:
            self.file_name = os.path.basename(self.file.name)
        if self.file:
            self.file_size = self.file.size
            
        # Set financial year based on upload date if not provided
        if not self.financial_year:
            current_date = datetime.now()
            if current_date.month >= 4:  # Financial year starts in April
                self.financial_year = f"{current_date.year}-{current_date.year + 1}"
            else:
                self.financial_year = f"{current_date.year - 1}-{current_date.year}"
                
        super().save(*args, **kwargs)

    def __str__(self):
        return self.file_name
