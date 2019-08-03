from django.db import models
from datetime import datetime
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField

# Create your models here.
class Posts(models.Model):
    title = models.CharField(max_length=200)
    # body = models.TextField()
    # body = RichTextField()
    body = RichTextUploadingField()
    created_at = models.DateTimeField(default=datetime.now, blank=True)
    author = models.CharField(max_length=200)
    # 'Post object' title fix
    def __str__(self):
        return self.title
    
    # 'Postss' plural fix
    class Meta:
        verbose_name_plural = "Posts"