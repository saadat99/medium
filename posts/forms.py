from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Posts, Profile


class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class PostForm(forms.ModelForm):

    class Meta:
        model = Posts
        fields = ('title', 'body',)

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email")

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("bio", "image",)

