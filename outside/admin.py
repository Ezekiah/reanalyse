from django.contrib import admin
from outside.models import Enquiry, Subscriber, Message, VizControl
from reanalyseapp.models import AccessRequest
from reanalyseapp.actions import  *


class MessageAdmin( admin.ModelAdmin ):
    search_fields = ['content']
    
class SubscriberAdmin( admin.ModelAdmin ):
    actions = [export_as_csv_action("CSV Export")]
    
class AccessRequestAdmin( admin.ModelAdmin ):
    search_fields = ['user__username']
    list_display = ('user', 'enquete', 'date', 'is_activated')
   

class VizControlAdmin( admin.ModelAdmin ):
    search_fields = ['enquete']
    list_display = ('enquete','classement', 'timeline', 'map')
    
admin.site.register(AccessRequest, AccessRequestAdmin )



admin.site.register( Enquiry )
admin.site.register( Subscriber, SubscriberAdmin )
admin.site.register( Message, MessageAdmin )
admin.site.register( VizControl, VizControlAdmin )
