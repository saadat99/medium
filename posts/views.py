from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
# importing post model
from .models import Posts
from .forms import NewUserForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import PostForm
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import random
from django.db.models.aggregates import Count


# Create your views here.
def index(request):
    # return HttpResponse('HELLO')
    posts = Posts.objects.all().order_by('-created_at')[:10]
    # Could slow database
    rand_posts = Posts.objects.all().order_by('?')[:2]
    context = {
        'posts': posts,
        'rand_posts': rand_posts
    }

    return render(request, 'posts/index.html', context)

def post_details(request, id):
    posts = Posts.objects.get(id=id)
    context = {
        'post' : posts
    }
    return render(request, 'posts/post_details.html', context)

def register(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"New account created: {username}")
            login(request, user)
            return redirect("homepage")
        else:
            for msg in form.error_messages:
                messages.error(request, f"{msg}:{form.error_messages[msg]}")

    form = NewUserForm
    return render(
        request,
        "posts/register.html",
        {"form": form}
    )

@login_required
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('details', post.pk)
    else:
        form = PostForm()

    form = PostForm()
    return render(request, 'posts/post_edit.html', {'form': form})

@login_required
def post_edit(request, pk):
    post = get_object_or_404(Posts, pk=pk)
    # Issue TODO
    if post.user != request.user:
        raise Http404  # or similar
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            # post.author = request.user
            # post.published_date = timezone.now()
            post.save()
            return redirect('details', post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'posts/post_edit.html', {'form': form})

def profile(request, username):
    # posts = Posts.objects.filter(user=request.user).order_by('-created_at')[:10]
    user = get_object_or_404(User, username=username)
    posts = Posts.objects.filter(user=user).order_by('-created_at')[:10]

    # Check for follow button
    # TODO more efficient way https://docs.djangoproject.com/en/dev/ref/models/querysets/#exists 
    follow_check = False
    if request.user.is_authenticated:
        if user.profile in request.user.profile.follows.all():
            follow_check = True
    
    context = {
        'title' : 'Latest Posts',
        'posts' : posts,
        'owner' : user,
        'follow_check' : follow_check        
    }
    return render(request, 'posts/profile.html', context)

def follow(request, username, action):
    user = get_object_or_404(User, username=username)
    
    print(action)
    if action:
        request.user.profile.follows.add(user.profile)
        return HttpResponse('added relation')
    else:
        request.user.profile.follows.remove(user.profile)
        return HttpResponse('removed relation')

    # context = {
    #     'title' : 'Latest Posts',
    #     'posts' : posts,
    #     'owner' : user        
    # }
    # return render(request, 'posts/profile.html', context)

@login_required
def settings(request):
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST ,instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f"Your account has been updated")
            return redirect("settings")
        else:
            for msg in form.error_messages:
                messages.error(request, f"{msg}:{form.error_messages[msg]}")
    
    u_form = UserUpdateForm(instance=request.user)
    p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form' : u_form,
        'p_form' : p_form
    }
    return render(request, 'posts/settings.html', context)