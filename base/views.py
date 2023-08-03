from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, Message
from .forms import RoomForm, UserForm
# from django.http import HttpResponse

# Create your views here.

# rooms = [
#     {'id': 1, 'name': 'Lets Learn Python'},
#     {'id': 2, 'name': 'Design Something'},
#     {'id': 3, 'name': 'Frontend Developer'},
#     {'id': 4, 'name': 'Backend Developer'},
# ]

# Creating a login page
def loginPage(request):
    page = 'login'

    # Restricting a logged in user from accessing the login route 
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        # Checking if the user exists in the database
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')
            
        # Authenticating the User
        user = authenticate(request, username=username, password=password)

        # Logging in the user if the user exists
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username OR Password does not exist')
            
    context = {'page': page}
    return render(request, 'base/login_register.html', context)

# Logging out our User
def logoutUser(request):
    logout(request)
    return redirect('home')
   
# Creating a Register functionality for our user
def registerPage(request):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "An error occurred during registration")
    return render(request, 'base/login_register.html', {'form':form})
    
# Creating a search bar for our home page 
def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |  
        Q(description__icontains=q)
        )

    topics = Topic.objects.all()[0:3]
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    # print(len(topics))

    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count, "room_messages": room_messages}
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()

    # A code for that handles the user comments 
    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room = room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
 
    context = {'room': room, 'room_messages':room_messages, 'participants': participants}
    return render(request, 'base/room.html',context)


#  This code here creates a Room
@login_required(login_url='login') # Checks if a user is logged in if false redirect to login page
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )
        # form = RoomForm(request.POST)
        # if form.is_valid():
        #    room = form.save(commit=False)
        # #    saving the user who creates a room as a host
        #    room.host = request.user
        #    room.save()
        return redirect('home')

    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)

def userProfile(request, pk):
    user = User.objects.get(id=pk) 
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context={'user': user, 'rooms': rooms, 'room_messages': room_messages, 'topics': topics}
    return render(request, 'base/profile.html', context)


# Updates the room information
@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse("You are not allowed here!!")

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        # form = RoomForm(request.POST, instance=room)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        # if form.is_valid():
        #     form.save()

        return redirect('home')

    context = {'form': form, 'topics':topics, 'room': room}
    return render(request, 'base/room_form.html', context)

# Deletes the room
@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    # print(Room.objects)
    if request.user != room.host:
        return HttpResponse("You are not allowed here!!")
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})

# Delete a user's message
@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    # Only the message owner can delete their message
    if request.user != message.user:
        return HttpResponse("You are not allowed to delete this message!")

    if request.method == "POST":
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': message})

# Edit a user's message
# @login_required(login_url='login')
# def editMessage(request, pk):
#     message = Message.objects.get(id=pk)

#     if request.user != message.user:
#          return HttpResponse("You are not allowed to edit this message!")

#     if request.method == "POST":
#         # message_body = request.POST.get('body')
#         message.body = request.POST.get('body')
#         message.save()
#         # form = MessageForm(request.POST, instance=message)
#         # if form.is_valid():
#         #     form.save()
#         return redirect('room')
    
#     context = {"message": message}
#     return render(request, 'base/room.html', context)

@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
            
    return render(request, 'base/update-user.html', {'form': form})

        
def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    rooms = Room.objects.all()
    

    return render(request, 'base/topics.html', {"topics": topics, "rooms": rooms})

def activyPage(request):
    room_messages = Message.objects.all()
    # room_messages = room.message_set.all()
    return render(request, 'base/activity.html', {"room_messages": room_messages})