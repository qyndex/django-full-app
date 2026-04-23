"""Forms for the accounts app — registration and profile editing."""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


class RegisterForm(UserCreationForm):
    """Extended registration form that also captures email."""

    email = forms.EmailField(required=True, help_text="A valid email address is required.")
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "password1", "password2"]

    def clean_email(self) -> str:
        email = self.cleaned_data["email"]
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email.lower()

    def save(self, commit: bool = True) -> User:
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data.get("first_name", "")
        user.last_name = self.cleaned_data.get("last_name", "")
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    """Form to edit bio, avatar, and website."""

    class Meta:
        model = Profile
        fields = ["bio", "avatar", "website"]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4}),
        }


class UserForm(forms.ModelForm):
    """Form to edit user's first/last name and email."""

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]

    def clean_email(self) -> str:
        email = self.cleaned_data["email"]
        qs = User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Another account uses this email.")
        return email.lower()
