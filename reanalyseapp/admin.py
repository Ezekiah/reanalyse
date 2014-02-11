# -*- coding: utf-8 -*-
############################################################
from django.contrib import admin
from reanalyseapp.models import *
from django.db import models
import settings
import codecs

from actions import export_as_csv_action

###########################################################################
# LOGGING
###########################################################################
import logging
logger = logging.getLogger('apps')
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
nullhandler = logger.addHandler(NullHandler())
###########################################################################






#############################################################
# FOR HTML CONTENTS (editable) 'SiteContent' model (for models.TextField())
############################################################
# class CommonMedia:
# 	js = (
# 		'https://ajax.googleapis.com/ajax/libs/dojo/1.6.0/dojo/dojo.xd.js',
# 		settings.MEDIA_URL+'/js/dojoRichEditor.js',
# 	)
# 	css = {
# 		'all': (
# 			settings.MEDIA_URL+'/css/admin.css',
# 			settings.MEDIA_URL+'/css/reanalyse.css',
# 		),
# 	}
#############################################################
class SiteContentAdmin(admin.ModelAdmin):
	fieldsets = [
		(None, { 'fields': ('name','lang','description','contenthtml')}),
	]
	#Media = CommonMedia
	# on list
	list_display = ('name','description','lang')
	def save_model(self, request, obj, form, change):
		logger.info("site-content saved on disk: ["+obj.lang+"] "+obj.name)
		filepath = settings.REANALYSESITECONTENTPATH + obj.name+'_content_'+obj.lang.lower()+'.html'
		fileOut = codecs.open(filepath,'w','utf-8')
		fileOut.write(obj.contenthtml)
		fileOut.close()
		obj.save()
#############################################################






#############################################################
# ENQUETES, TEXTES, ...
#############################################################
class TexteAdmin(admin.ModelAdmin):
    list_display = ('name','contenttxt', 'locationpath', 'enquete', 'location', 'description')
    search_fields = ['name', 'locationpath']
# 	Media = CommonMedia
#############################################################

class TagAdmin(admin.ModelAdmin):
	search_fields = ['name']



from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

UserAdmin.list_display = ('email', 'first_name', 'last_name', 'is_active', 'date_joined', 'is_staff')
UserAdmin.actions = [export_as_csv_action("CSV Export")]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)



# Tag
admin.site.register( Tag, TagAdmin )


# Texte aka study documents
admin.site.register( Texte, TexteAdmin )




#############################################################

admin.site.register(SiteContent, SiteContentAdmin) # tryout to edit html contents using admin
admin.site.register(Enquete)

############################################################



