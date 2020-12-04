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