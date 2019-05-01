from django.shortcuts import render
from django.http import HttpResponse
# importing post model
from .models import Posts

# Create your views here.
def index(request):
    # return HttpResponse('HELLO')
    posts = Posts.objects.all()[:10]
    context = {
        'title' : 'Latest Posts',
        'posts' : posts
    }

    return render(request, 'posts/index.html', context)

def details(request, id):
    posts = Posts.objects.get(id=id)
    context = {
        'post' : posts
    }

    return render(request, 'posts/details.html', context)
