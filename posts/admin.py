from django.contrib import admin

# Register your models here.
from .models import Posts, Profile

admin.site.register(Posts)
admin.site.register(Profile)