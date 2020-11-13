from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout

# Create your views here.
def index(request):
    return render(request,'index.html',{})
    
def register_user(request):
    if request.method=='POST':
        try:
            prevuser=User.objects.get(username=request.POST['username'])
            return render(request,'register.html',{'error_message':"User already exists!!"})
        except User.DoesNotExist:
            if request.POST['password']==request.POST['password2']:
                user=User.objects.create_user(request.POST['username'],request.POST['email'],request.POST['password'])
                user.last_name=request.POST['lname']
                user.first_name=request.POST['fname']
                user.save()
                return redirect('/userauth/login')
            else:
                return render(request,'register.html',{'error_message':"Passwords do not match!!"})
    return render(request,'register.html',{})

def login_user(request):
    if request.method=='POST':
        user = authenticate(request,username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            login(request,user)
            return redirect('/userauth/home')
        else:
            return render(request,'login.html',{'error_message':"Incorrect username or password"})

    return render(request,'login.html',{})
    
def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
      
    return redirect('/userauth')


def home(request):
    if request.user.is_authenticated:
        return render(request,'home.html',{'user':request.user})
    else:
        return redirect('/userauth/login')