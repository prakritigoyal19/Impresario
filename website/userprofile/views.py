from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from scheduling.models import Organization,User,Membershiplevel,Teamrequest, Event
from gsetup import service, google_create_event, google_update_event  
import datetime
from .utils import is_time_between
# Create your views here.
import pytz

utc=pytz.UTC
def create_team(request,par_id) :

    if request.user.is_authenticated:
        warning = ''
        if request.method == 'POST':
            team_name = request.POST['team_name']
            members = request.POST.getlist('checks')
            user=request.user
            description = request.POST['description']
            if Organization.objects.filter(name = team_name,parent_org__id = par_id).exists():
                warning = "team with that name already exists"
            elif Membershiplevel.objects.get(user_id = request.user.id,organization_id = par_id).role == 1 : #If user is an admin
                org = Organization.objects.create(name = team_name,parent_org_id = par_id)
                members = User.objects.filter(pk__in = members)
                #Membershiplevel.create_team(members,org,par_id)
                Membershiplevel.create_team(members,org,par_id,request.user.id)
                warning = "team created"
            else :
                Teamrequest.create_team_req(user,team_name,description,par_id,members) #If user is a participant
                warning = "team request sent to admin"
        memberships = Membershiplevel.objects.filter(organization__id = par_id)
        return render(request,'create_team.html',{'memberships':memberships,'warning':warning,'user':request.user},)
    else:
        return redirect('/userauth/login')

def create_new_team(request):

    if request.user.is_authenticated:
        warning = ''
        if request.method == 'POST':
            team_name = request.POST['team_name']
            members = request.POST.getlist('checks')
            user=request.user
            description = request.POST['description']
            if Organization.objects.filter(name = team_name,parent_org__id = None).exists():
                warning = "team with that name already exists"
            else:
                org = Organization.objects.create(name = team_name,parent_org_id = None)
                members = User.objects.filter(pk__in = members)
                Membershiplevel.create_team(members,org,None,request.user.id)
                #Membershiplevel.create_team(members,org,par_id)
                warning = "team created"
        memberships = Membershiplevel.objects.all()
        print(memberships)
        return render(request,'create_team.html',{'memberships':memberships,'warning':warning,'user':request.user},)
    else:
        return redirect('/userauth/login')

def team_request(request, par_id) :
    if request.user.is_authenticated:
        user = request.user
        top_org = Organization.get_top_org(par_id)
        all_sub_org = Organization.get_all_children(top_org)
        sub_org = Membershiplevel.get_subgroups(all_sub_org, user)
        tr_request = Teamrequest.objects.filter(par_org__in = sub_org, status = 2) 
        print(tr_request) 
        return render(request,'team_request.html',{'team_request':tr_request,'user':request.user })
    else:
        return redirect('/userauth/login')

def ajax_change_status(request):
    if request.user.is_authenticated:
        request_status = request.GET.get('request_status', 2)
        request_id = request.GET.get('request_id', False)
        team_request = Teamrequest.objects.get(pk=request_id)
        try:
            request_status = int(request_status)
            if team_request.status == 1 :
                return JsonResponse({"success": True,"status":"already approved"})
            elif team_request.status == 0 :
                return JsonResponse({"success": True,"status":"already rejected"})
            elif request_status == 1:
                team_request.status=1
                team_request.save()
                return JsonResponse({"success": True,"status":"approved"})
            elif request_status == 0:
                team_request.status = 0
                team_request.save()
                return JsonResponse({"success": True,"status":"rejected"}) 
        except Exception as e:
            return JsonResponse({"success": False})
    else:
        return redirect('/userauth/login')


def show_team(request, team_id):
    if request.user.is_authenticated:
        user = request.user
        org  = Organization.objects.get(pk = team_id)
        if not org:
            return  redirect('/userauth/home')
        children = Organization.get_all_children(org)
        members = Membershiplevel.objects.filter(organization__id = org.id)
        print(org.event.all())
        return render(request, 'show_team.html',{"org": org, "children": children, "members": members,'user':request.user})
    else:
        return redirect('/userauth/login')

def add_event(request, org_id):
    if request.user.is_authenticated:
        user = request.user
        org  = Organization.objects.get(pk = org_id)
        if not org:
            return redirect('/userprofile/create_team/1')
        if request.method == 'POST':
            start_date = request.POST['start-date']
            start_time = request.POST['start-time']
            end_date = request.POST['end-date']
            end_time = request.POST['end-time']
            start = str(start_date) +" "+str(start_time)
            end = str(end_date) +" "+str(end_time)
            title = request.POST['title']
            start = datetime.datetime.strptime(start, "%Y-%m-%d %H:%M")
            end= datetime.datetime.strptime(end, "%Y-%m-%d %H:%M")
            start.replace(tzinfo=utc)
            start = pytz.utc.localize(start)
            end.replace(tzinfo=utc)
            end = pytz.utc.localize(end)
            description = request.POST['description']
            location = request.POST['location']
            all_events = Event.objects.all()
            clash_events = []
            # for e in all_events:
            #     if is_time_between(start,end, e.start_time) or is_time_between(start,end, e.end_time) or is_time_between(e.start_time,e.end_time, end) or is_time_between(e.start_time,e.end_time, start):
            #         clash_events.append(e)

            members = Membershiplevel.objects.filter(organization = org).values('user')
    
            # for c in clash_events:
            #     org2  = c.organization
            #     mem2 = Membershiplevel.objects.filter(organization = org2).values('user')
            #     for m in mem2:
            #         if m in members:
            #             return render(request,'add_event.html',{"warning": "Clashes!!!!","org":org})
            attendees = []
           
            for m in members:
                print(m)
                user = User.objects.get(pk = m['user'])
                attendees.append({"email": user.email})
            event = google_create_event(location, title, description, start,end,"tentative", attendees)
            if event['id']:
                new_event = Event.objects.create(organization = org, title= title, description= description, location = location, start_time = start, end_time = end, status = 0, eventId = event['id'] )
                new_event.save()
                return render(request,"add_event.html",{"warning": "Success", "org":org,'user':request.user})
            else:
                return render(request,"add_event.html",{"warning": "Failure","org":org,'user':request.user })
        else:
            return render(request, 'add_event.html', {"org": org,'user':request.user})
    else:
        return redirect('/userauth/login')

def view_event(request, event_id):
    if not request.user.is_authenticated:
        return redirect('/userauth/login')

    print(event_id)
    event = Event.objects.get(pk=event_id)
    if not event:   
        return redirect('userprofile/view_team/1')
    members = Membershiplevel.objects.filter(organization = event.organization.id).values('user')
    attendees = User.objects.filter(pk__in = members)
    return render(request,'show_event.html', {'event': event , 'attendees': attendees,'user':request.user})

def update_event(request,event_id):
    if not request.user.is_authenticated:
        return redirect('/userauth/login')

    event = Event.objects.get(pk = event_id)
    if not event:
        return redirect('userprofile/view_team/1')
    if request.method == 'POST':
        title = request.POST['title']
        location = request.POST['location']
        description = request.POST['description']
        start_date = request.POST['start-date']
        start_time = request.POST['start-time']
        end_date = request.POST['end-date']
        end_time = request.POST['end-time']
        start = str(start_date) +" "+str(start_time)
        end = str(end_date) +" "+str(end_time)
        # print(len(start))
        # print(len(end))
        start = datetime.datetime.strptime(start, "%Y-%m-%d %H:%M")
        end = datetime.datetime.strptime(end, "%Y-%m-%d %H:%M")
        status  = request.POST['status']
        if status==0:
            status = "tentative"
        elif status==1:
            status = "cancelled"
        else:
            status = "confirmed"
        updated_event  = google_update_event(event.eventId, title, description, location, start, end, status)
        # print(updated_event)
        if not updated_event.get('id'):
            return render(request, 'update_event.html', {"event": event,'user':request.user})

        event.eventId = updated_event['id']
        event.title = updated_event['summary']
        event.location = updated_event['location']
        event.description = updated_event['description']
        if status == "tentative":
            event.status=0
        elif status == "cancelled":
            event.status=1
        else:
            event.status=2
       
        
        event.start_time = start
             
        event.end_time =  end
        print("event.start_time")
        print(event.start_time)
        print("event.end_time")
        print(event.end_time)
        print(event)
        event.save()
        return redirect('/userprofile/view_event/'+str(event.id))
    return render(request, 'update_event.html', {"event": event,'user':request.user})

def view_calendar(request):
    if not request.user.is_authenticated:
        return redirect('/userauth/login')
    return render(request,'calendar.html',{'user':request.user})