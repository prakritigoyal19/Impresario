from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Organization(models.Model):
    name = models.CharField(blank = False, max_length = 100)
    parent_org = models.ForeignKey('self',default = None, null = True, blank = True, on_delete = models.CASCADE)
    def __str__(self):
        if self.parent_org:
            parent = "-"+self.parent_org.name
        else:
            parent = ""
        return self.name+parent
    @classmethod
    def get_top_org(self,id):
        par = self.objects.get(pk=id)
        while par.parent_org is not None :
                par = par.parent_org
        return par
    @classmethod
    def get_all_children(self,par):
        q = [par]
        children = [par]
        while q :
            curr = q.pop()
            curr_children = self.objects.filter(parent_org = curr)
            q += curr_children
            children += curr_children
        return children
        
class Groups(models.Model):
    organization = models.ForeignKey(Organization,null=True, on_delete = models.CASCADE, related_name = 'parent')
    group = models.ForeignKey(Organization,null=True, on_delete = models.CASCADE, related_name = 'child')

class Membershiplevel(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete = models.CASCADE)
    ADMIN = 1
    PARTICIPANT = 2
    ROLE = (
        (ADMIN, 'admin'),
        (PARTICIPANT, 'participant')
    )
    role = models.IntegerField(choices = ROLE)
    hierarchy = models.IntegerField(null=True)

    def __str__(self):
        return self.user.username+"-"+self.organization.name

    @classmethod
    def create_team(self,members,org,par_id):
        for member in members :
            role_in_par=self.objects.get(user_id=member.id,organization_id=par_id)
            m = self.objects.create(user=member,organization=org,hierarchy=role_in_par.hierarchy,role=role_in_par.role)
            print(m)
    @classmethod
    def get_subgroups(self, groups, user):
        subgroups = []
        for group in groups:
            try :
                role_in_group = self.objects.get(organization_id = group.id,user_id = user.id).role
                if role_in_group == 1:
                    print(group,subgroups)
                    subgroups.append(group)
            except self.DoesNotExist :
                continue
        return subgroups

class Teamrequest(models.Model):
    REJECTED=0
    APPROVED=1
    PENDING=2
    STATUS=(
        (REJECTED,"Rejected"),
        (APPROVED,"Approved"),
        (PENDING,"Pending")
    )
    sender = models.ForeignKey(User,on_delete=models.CASCADE,related_name='sender')
    team_name = models.CharField(blank=False,max_length=100)
    team_description = models.CharField(blank=False,max_length=500)
    team_members = models.ManyToManyField(User,blank=True)
    par_org = models.ForeignKey(Organization,on_delete=models.CASCADE)
    status = models.IntegerField(choices=STATUS,default=PENDING)
    def __str__(self):
        par=self.par_org
        team_name=""
        while par :
            team_name=(par.name+'/')+team_name
            par=par.parent_org
        return team_name+ self.team_name
    @classmethod
    def create_team_req(self,user,team_name,description,par_id,members):
        tr=self.objects.create(sender=user,team_name=team_name,team_description=description,par_org_id=par_id)
        tr.team_members.set(members)
        tr.save()
        print(tr)

class Event(models.Model):
    eventId = models.TextField(blank=False)
    title = models.CharField(blank=False,max_length=100)
    description = models.CharField(blank=False,max_length=500)
    location = models.CharField(max_length=100)
    Tentative=0
    Cancelled=1
    Confirmed=2
    STATUS=(
        (Tentative,"tentative"),
        (Cancelled,"cancelled"),
        (Confirmed,"Confirmed")
    )
    status = models.IntegerField(choices= STATUS, blank=False,max_length=500)
    organization = models.ForeignKey(Organization,on_delete=models.CASCADE,related_name='event')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return self.title
