from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic
from .forms import RoomForm

# rooms=[
#     {'id':1, 'name':'Lets Learn Python!'},
#     {'id':2, 'name':'Design with me'},
#     {'id':3, 'name':'FrontEnd Developers'},
#
# ]


def loginPage(request):
    page = 'login'
    if request.user.is_authenticated: #user login qibogan bosa posiskda /login/ dib yozsa login sahifasiga obormidi. Home da qoladi
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username').lower()#username & passwordni olib
        password = request.POST.get('password')

        try:                                    #mavjud & mavjudmasligini tekshir
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, username=username, password=password)#mavjud bo'lsa o'tkaz

        if user is not None:
            login(request, user)#created user
            return redirect('home')
        else:
            messages.error(request, 'Username or Password does not exist')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')


def registerPage(request):
    form = UserCreationForm()

    if request.method == 'POST':#we pass user data
        form = UserCreationForm(request.POST) # user creationformga uzatamiz
        if form.is_valid(): #we check form is valid
            user = form.save(commit=False) #agar o'sha bo'lsa
            user.username = user.username.lower()# username kicik harfdaligini tekwiramiz
            user.save() # userni saqlimiz
            login(request, user) # userni login qilamiz
            return redirect('home') #va home ga yuboramiz
        else:
            messages.error(request, 'An error occurred during registration')

    return render(request, 'base/login_register.html', {'form': form})

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    rooms = Room.objects.filter(
        Q(topic__name__icontains = q) |
        Q(name__icontains=q)|
        Q(description__icontains=q)
    )

    topics = Topic.objects.all()
    room_count = rooms.count()

    context = {'rooms':rooms, 'topics': topics, 'room_count':room_count} #contextda topiclani >>Topics<< soziga biriktrildi
    return render(request, 'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    context = {'room':room, 'room_messages': room_messages}
    return render(request,'base/room.html', context)

@login_required(login_url='login')#login in qimagan bosa room yaratomidi  #restricted pages == cheklangan sahifalar
def createRoom(request):
    form = RoomForm()

    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
                form.save()
                return redirect('home')

    context = {'form':form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login') #restricted pages == cheklangan sahifalar
def updateRoom(request, pk):#login in qimagan bosa room yangilomidi
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    if request.user != room.host: # user ozi admin bomagan roomni ediq qimoqci bosa sizga ruxsat berilmagan dip qaytaradi.
        return HttpResponse('You are not allowed here!')

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form':form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')#login in qimagan bosa roomni o'chiromidi #restricted pages == cheklangan sahifalar
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host: # user ozi admin bomagan roomni delete qmoqci bosa sizga ruxsat berilmagan dip qaytaradi.
        return HttpResponse('You are not allowed here!')

    if request.method == 'POST':
            room.delete()
            return redirect('home')
    return render(request, 'base/delete.html', {'obj':room})


