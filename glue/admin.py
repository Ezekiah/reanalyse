from django.contrib import admin
from glue.models import Page, Pin




class PinAdmin( admin.ModelAdmin ):
    search_fields = ['title','enquiry']
    list_display = ('date_last_modified','parent')
    
admin.site.register( Page )
admin.site.register( Pin, PinAdmin )