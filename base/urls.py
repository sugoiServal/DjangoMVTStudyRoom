from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("room/<str:pk>/", views.room, name="room"),
    path("topics/", views.topicsPage, name="topics-page"),
    path("activities/", views.activitiesPage, name="activities-page"),
    path("profile/<str:pk>/", views.userProfile, name="user-profile"),
    path("create-room/", views.createRoom, name="create-room"),
    path("update-room/<str:pk>/", views.updateRoom, name="update-room"),
    path("delete-room/<str:pk>/", views.deleteRoom, name="delete-room"),
    path("logout/", views.logoutUser, name="logout"),
    path("login/", views.loginUser, name="login"),
    path("register/", views.registerUser, name="register"),
    path("edit-user/", views.editUser, name="edit-user"),
    path("delete-message/<str:pk>/", views.deleteMessage, name="delete-message"),
]
