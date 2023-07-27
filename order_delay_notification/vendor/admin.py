from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Vendor)
admin.site.register(Trip)
admin.site.register(DelayReport)
admin.site.register(Order)
admin.site.register(Agent)
admin.site.register(AgentOrder)