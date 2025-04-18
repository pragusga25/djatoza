from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import User
from .forms import UserUpdateForm, ProfileUpdateForm
from .models import UserProfile, LoginLog


@login_required
def profile_view(request):
    """Display user profile page"""
    return render(request, "main/profile.html")


@login_required
def profile_edit(request):
    """Allow user to edit their profile"""
    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile has been updated!")
            return redirect("profile")
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {"user_form": user_form, "profile_form": profile_form}
    return render(request, "main/profile_edit.html", context)


@login_required
def map_view(request):
    """Display full screen map showing all users' locations"""
    return render(request, "main/map.html")


@login_required
def get_user_locations(request):
    """API endpoint to get all user locations as JSON"""
    # Get all users who have profiles with coordinates
    users = User.objects.filter(
        profile__latitude__isnull=False, profile__longitude__isnull=False
    ).select_related("profile")

    data = []

    for user in users:
        # Only include users with valid coordinates
        if user.profile.latitude is not None and user.profile.longitude is not None:
            data.append(
                {
                    "id": user.id,
                    "username": user.username,
                    "latitude": float(user.profile.latitude),
                    "longitude": float(user.profile.longitude),
                    "name": (
                        f"{user.first_name} {user.last_name}".strip()
                        if user.first_name or user.last_name
                        else user.username
                    ),
                }
            )

    return JsonResponse(data, safe=False)


@login_required
def user_popup(request, user_id):
    """Return user profile popup content for the map"""
    # Only superusers can view other users' profiles
    if not request.user.is_superuser and request.user.id != int(user_id):
        return JsonResponse({"error": "Permission denied"}, status=403)

    try:
        user = User.objects.get(id=user_id)
        profile = user.profile

        data = {
            "username": user.username,
            "email": user.email,
            "name": f"{user.first_name} {user.last_name}".strip() or user.username,
            "address": profile.address or "",
            "phone": profile.phone_number or "",
        }

        return JsonResponse(data)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)


def log_user_login(sender, user, request, **kwargs):
    """Log user login activity"""
    LoginLog.objects.create(user=user, action="login")


def log_user_logout(sender, user, request, **kwargs):
    """Log user logout activity"""
    if user:  # Anonymous user check
        LoginLog.objects.create(user=user, action="logout")
