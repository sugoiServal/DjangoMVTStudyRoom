from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages as MSG
from .models import Room, Topic, Message
from .forms import RoomForm, UserForm

# from .forms import RoomForm, MyUserCreationForm, UserForm


def home(req):
    q = req.GET.get("q") if req.GET.get("q") != None else ""
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q)
    )
    topics = Topic.objects.all()[:5]
    messages_activities = Message.objects.filter(
        Q(room__topic__name__icontains=q)
    ).order_by("-created")[:10]

    context = {
        "rooms": rooms,
        "topics": topics,
        "room_count": rooms.count(),
        "activities": messages_activities,
    }
    return render(req, "base/home.html", context)


def topicsPage(req):
    q = req.GET.get("q") if req.GET.get("q") != None else ""
    topics = Topic.objects.filter(Q(name__icontains=q))
    return render(req, "base/topics.html", {"topics": topics})


def activitiesPage(req):
    messages_activities = Message.objects.all().order_by("-created")[:4]
    return render(req, "base/activity.html", {"activities": messages_activities})


def room(req, pk):
    room = Room.objects.get(id=pk)
    messages = room.message_set.all().order_by("-created")
    participants = room.participants.all()

    if req.method == "POST":
        if len(req.POST.get("body")) < 3:
            MSG.error(req, "Please provide at least 3 characters.")
            return redirect("room", pk=room.id)

        message = Message.objects.create(
            user=req.user, room=room, body=req.POST.get("body")
        )
        room.participants.add(req.user)
        return redirect("room", pk=room.id)
    context = {
        "pk": pk,
        "room": room,
        "comments": messages,
        "participants": participants,
    }
    return render(req, "base/room.html", context)


def userProfile(req, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    messages_activities = user.message_set.all().order_by("-created")
    topics = Topic.objects.all()

    context = {
        "user": user,
        "rooms": rooms,
        "activities": messages_activities,
        "topics": topics,
    }
    return render(req, "base/profile.html", context)


@login_required(login_url="/login")
def createRoom(req):
    # either populate an empty form to template or save to model from req form data(POST)

    # for template
    form = RoomForm()
    context = {"form": form}

    # for save to model
    if req.method == "POST":
        form = RoomForm(req.POST)
        print(form)
        if form.is_valid():  # do form vaildation based on model
            room = form.save(commit=False)
            room.host = req.user
            room.save()
            return redirect("home")

    return render(req, "base/room_form.html", context)


@login_required(login_url="/login")
def updateRoom(req, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)  # prefill the form with the target record

    if req.user != room.host:
        return HttpResponse("You are not the owner of the room.")

    # for save to model
    if req.method == "POST":
        form = RoomForm(req.POST, instance=room)  # instance specify the target record
        if form.is_valid():  # do form vaildation based on model
            form.save()
            return redirect("home")

    context = {"form": form}
    return render(req, "base/room_form.html", context)


@login_required(login_url="/login")
def deleteRoom(req, pk):
    room = Room.objects.get(id=pk)

    if req.user != room.host:
        return HttpResponse("You are not the owner of the room.")

    # delete
    if req.method == "POST":
        room.delete()
        return redirect("home")

    return render(req, "base/delete.html", {"obj": room})


def loginUser(req):
    if req.user.is_authenticated:
        return redirect("home")
    if req.method == "POST":
        username = req.POST.get("username").lower()
        password = req.POST.get("password")
        try:
            user = User.objects.get(username=username)
        except:
            MSG.error(req, "User does not exist")
        user = authenticate(req, username=username, password=password)
        if user is not None:
            login(req, user)
            return redirect("home")
        else:
            MSG.error(req, "The password does not match.")

    context = {"page": "login"}
    return render(req, "base/login_register.html", context)


def logoutUser(req):
    logout(req)
    return redirect("home")


def registerUser(req):
    if req.user.is_authenticated:
        return redirect("home")
    form = UserCreationForm()

    if req.method == "POST":
        form = UserCreationForm(req.POST)
        print(req.POST)
        print(form.is_valid())
        if form.is_valid():  # do form vaildation based on model
            user = form.save(
                commit=False
            )  # do not commit to db at this time, check username case first
            user.username = user.username.lower()
            user.save()
            login(req, user)
            return redirect("home")
        else:
            MSG.error(req, "An error occurs during registration.")

    context = {"page": "register", "form": form}
    return render(req, "base/login_register.html", context)


@login_required(login_url="/login")
def editUser(req):
    user = req.user
    form = UserForm(instance=user.userinfo)
    # for save to model
    if req.method == "POST":
        form = UserForm(
            req.POST, req.FILES, instance=user.userinfo
        )  # instance specify the target record
        if form.is_valid():  # do form vaildation based on model
            form.save()
            return redirect("user-profile", pk=user.id)
    return render(req, "base/edit-user.html", {"form": form})


@login_required(login_url="/login")
def deleteMessage(req, pk):
    message = Message.objects.get(id=pk)

    if req.user != message.user:
        return HttpResponse("You are not the owner of the room.")

    # delete
    if req.method == "POST":
        message.delete()
        return redirect("room", pk=message.room.id)

    return render(req, "base/delete.html", {"obj": message})
