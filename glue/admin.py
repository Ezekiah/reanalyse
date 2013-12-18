from django.contrib import admin
from glue.models import Page, Pin


def pin_title(obj):
    return "%s (%s) a.k.a. %s" % (obj.slug, obj.language, obj.title)
    


class PinAdmin( admin.ModelAdmin ):
    search_fields = ['title','enquiry']
    list_display = (pin_title, 'slug','date_last_modified','parent')
    
admin.site.register( Page )
admin.site.register( Pin, PinAdmin )