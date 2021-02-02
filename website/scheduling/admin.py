from django.contrib import admin
from .models import Organization, Groups, Membershiplevel, Teamrequest, GroupEvent
from swingtime import models as swingtime
# Register your models here.
from swingtime import models as swingtime
admin.site.register(Organization)
admin.site.register(Groups)
admin.site.register(Membershiplevel)
admin.site.register(Teamrequest)
admin.site.register(GroupEvent)
admin.site.register(swingtime.Event)
