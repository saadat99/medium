from django.db import models
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from django.conf import settings
from django.contrib.auth.models import User
from PIL import Image

# Create your models here.
class Posts(models.Model):
    title = models.CharField(max_length=200)
    # body = models.TextField()
    # body = RichTextField()
    body = RichTextUploadingField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, default=1, on_delete=models.CASCADE)
    # 'Post object' title fix
    def __str__(self):
        return self.title
    
    # Plural fix 'Postss' 
    class Meta:
        verbose_name_plural = "Posts"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    bio = models.TextField(max_length=1000, blank=True)
    follows = models.ManyToManyField('Profile', related_name='followed_by', symmetrical=False)

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, **kwargs):
        super().save()
        # TODO remove old files, djang-cleanup suggested
        img = Image.open(self.image.path)
        size = 300

        if img.height > size or img.width > size:
            output_size = (size, size)
            img.thumbnail(output_size)
            img.save(self.image.path)
