# models.py
from django.db import models
from django.contrib.auth.models import User

class MessageVault(models.Model):
    title = models.CharField(max_length=100)
    encrypted_content = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    unlock_after = models.DateTimeField(null=True, blank=True)
    passphrase_hash = models.CharField(max_length=255, blank=True)
    salt = models.CharField(max_length=255, blank=True)
    encrypted_key = models.TextField(blank=True, null=True)
    self_destruct = models.BooleanField(default=False)
    has_been_viewed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} - {self.created_by.username}"