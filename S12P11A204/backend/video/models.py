from django.db import models

class Video(models.Model):
    title = models.CharField(max_length=100)
    file_url = models.URLField(max_length=200)  
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
