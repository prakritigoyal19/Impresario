from django.contrib import admin
from .models import Organization, Groups, Membershiplevel

# Register your models here.
admin.site.register(Organization)
admin.site.register(Groups)
admin.site.register(Membershiplevel)