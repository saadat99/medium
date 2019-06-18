from django.shortcuts import render, redirect
from django.http import HttpResponse
# importing post model
from .models import Posts
from .forms import NewUserForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import PostForm
from django.shortcuts import get_object_or_404


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

def logout_request(request):
    logout(request)
    messages.info(request, "You logged out")
    return redirect('homepage')

def login_request(request):
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}")
                return redirect('/')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(
        request = request,
        template_name = "posts/login.html",
        context={"form":form}
    )

def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            # post.published_date = timezone.now()
            post.save()
            return redirect('details', post.pk)
    else:
        form = PostForm()

    form = PostForm()
    return render(request, 'posts/post_edit.html', {'form': form})

def post_edit(request, pk):
    post = get_object_or_404(Posts, pk=pk)
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

