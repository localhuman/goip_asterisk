from django.contrib import admin
from django.contrib.admin import ModelAdmin


from sms.models import AppService,SIPTerminus,SMSIn,SMSOut,InboundError


class SMSOutAdmin(admin.ModelAdmin):
    model=SMSOut
    list_display=['text','fromNumber','toNumber','status','date','failure_reason']
    search_fields = ['toNumber','text']
    list_filter = ['fromNumber','status']

class SMSInAdmin(admin.ModelAdmin):
    model=SMSIn
    list_display = ['text','fromNumber','toNumber','date']
    search_fields = ['text','fromNumber']
    list_filter = ['toNumber']

class SIPTerminusAdmin(admin.ModelAdmin):
    model=SIPTerminus
    list_display = ['name','number','region','user','host','app']

# Register your models here.
admin.site.register(AppService,ModelAdmin)
admin.site.register(SIPTerminus,SIPTerminusAdmin)
admin.site.register(SMSIn,SMSInAdmin)
admin.site.register(SMSOut,SMSOutAdmin)
admin.site.register(InboundError,ModelAdmin)