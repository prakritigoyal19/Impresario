from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from userauth.models import Profile, Account
from scheduling.models import Organization,User,Membershiplevel,Teamrequest

# Create your views here.

def create_team(request,par_id) :

    if request.user.is_authenticated:
        warning = ''
        if request.method == 'POST':
            team_name = request.POST['team_name']
            members = request.POST.getlist('team_mem')
            user=request.user
            description = request.POST['description']
            if Organization.objects.filter(name = team_name,parent_org__id = par_id).exists():
                warning = "team with that name already exists"
            elif Membershiplevel.objects.get(user_id = request.user.id,organization_id = par_id).role == 1 : #If user is an admin
                org = Organization.objects.create(name = team_name,parent_org_id = par_id)
                members = User.objects.filter(pk__in = members)
                Membershiplevel.create_team(members,org,par_id)
                warning = "team created"
            else :
                Teamrequest.create_team_req(user,team_name,description,par_id,members) #If user is a participant
                warning = "team request sent to admin"
        memberships = Membershiplevel.objects.filter(organization__id = par_id)
        return render(request,'create_team.html',{'memberships':memberships,'warning':warning},)
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
        return render(request,'team_request.html',{'team_request':tr_request })
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
   