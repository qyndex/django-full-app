"""Views for the accounts app — register, profile view/edit."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import User

from .forms import ProfileForm, RegisterForm, UserForm


def register(request):
    """Registration view — creates User + Profile via signal."""
    if request.user.is_authenticated:
        return redirect("article-list")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created! You can now log in.")
            return redirect("accounts:login")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


@login_required
def profile(request):
    """View and edit the logged-in user's profile."""
    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("accounts:profile")
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)

    return render(
        request,
        "accounts/profile.html",
        {"user_form": user_form, "profile_form": profile_form},
    )


def public_profile(request, username: str):
    """Public profile page for any user."""
    user = get_object_or_404(User, username=username)
    articles = user.articles.filter(status="published").order_by("-created_at")[:5]
    return render(
        request,
        "accounts/public_profile.html",
        {"profile_user": user, "articles": articles},
    )
