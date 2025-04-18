from django.urls import path
from . import views

urlpatterns = [
    path("", views.map_view, name="map"),
    path("profile/", views.profile_view, name="profile"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
    path("api/locations/", views.get_user_locations, name="user_locations"),
    path("api/user/<int:user_id>/popup/", views.user_popup, name="user_popup"),
]
