from django.db import models
class Member(models.Model):
    username = models.CharField(max_length=80, unique=True)
    # A02 VULNERABILITY: passwords are stored as plaintext in this column.
    password = models.CharField(max_length=255)
    def __str__(self): return self.username

class Entry(models.Model):
    owner = models.ForeignKey(Member, on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.title
