# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('reanalyse',
	# set langage redirect view
	(r'^i18n/', include('django.conf.urls.i18n')),
	url(r'^admin/', include(admin.site.urls)),
	
	(r'^$', 'reanalyseapp.views.home'),
	
	#(r'^account/login/$', 'reanalyseapp.views.home'), # deprecated : loginview is set in settings.py
	(r'^account/logout/$', 'reanalyseapp.views.logoutuser'),
	
	######################################################################################################
	########## STREAMS & FILE REQUESTS
	
	(r'^stream/(?P<eid>\d+)/(?P<path>[-\._\w\d\/]+\.(mp3|ogg))+', 'reanalyseapp.views.stream'),
	(r'^getesereport/(?P<eid>\d+)', 'reanalyseapp.views.getEseReport'),		# ESE report download
	(r'^graph/download/(?P<gid>\d+)', 'reanalyseapp.views.downloadGraph'),
	(r'^graph/serve/(?P<gid>\d+).gexf', 'reanalyseapp.views.serveGraph'),	# for gexf display (sigma?)
	(r'^graph/serve/(?P<did>\d+).pdf', 'reanalyseapp.views.servePdf'),		# for simple pdf display
	
	######################################################################################################
	########## ENQUETES
	(r'^e/$', 'reanalyseapp.views.eBrowse'),
	(r'^e/admin$', 'reanalyseapp.views.eAdmin'),						# ADMIN PAGE : upload !
	(r'^e/add$', 'reanalyseapp.views.eAddAjax'),						# ajax-ADD (upload one file at a time)
	(r'^e/reset$', 'reanalyseapp.views.eReset'),						# RESET (erase temp upload folder)
	(r'^e/parse$', 'reanalyseapp.views.eParse'),						# PARSE (once all files uploaded in a specific folder)
	(r'^e/(?P<eid>\d+)/delete$', 'reanalyseapp.views.eDelete'),			# DELETE
	
	(r'^e/(?P<eid>\d+)/makealltfidf$', 'reanalyseapp.views.resetAllTfidf'),		# TFIDF ngrams

	(r'^e/solrclear$', 'reanalyseapp.views.eSolrIndexClear'),	# clear whole solr index
	(r'^e/solrupdate$', 'reanalyseapp.views.eSolrIndexUpdate'),	# update whole solr index
	
	(r'^e/export$', 'reanalyseapp.views.exportEnquetes'),		# unused yet
	(r'^e/delete$', 'reanalyseapp.views.deleteEnquetes'),
	
	########## 1.Overview
	(r'^e/(?P<eid>\d+)/$', 'reanalyseapp.views.eShow'),					# SHOW ENQUETE MAIN OVERVIEW

	########## 2.Enquete sur Enquete
	(r'^e/(?P<eid>\d+)/ese/$', 'reanalyseapp.views.eseShow'),			# SHOW ENQUETE SUR ENQUETE
	
	########## 3.Documents
	(r'^e/(?P<eid>\d+)/$', 'reanalyseapp.views.edBrowse'),
	(r'^e/(?P<eid>\d+)/d/$', 'reanalyseapp.views.edBrowse'),
	(r'^e/(?P<eid>\d+)/d/(?P<did>\d+)/$', 'reanalyseapp.views.edShow'),				# DOC normal
	(r'^e/(?P<eid>\d+)/dx/(?P<did>\d+)/$', 'reanalyseapp.views.edXmlShow'),			# DOC html only using xslt
	(r'^e/(?P<eid>\d+)/d/(?P<did>\d+)/parse$', 'reanalyseapp.views.edParseXml'),			# TEI only : build objects from XML structure
	(r'^e/(?P<eid>\d+)/d/(?P<did>\d+)/get$', 'reanalyseapp.views.dGetHtmlContent'),			# TEI get html content SENTENCE
	(r'^e/(?P<eid>\d+)/d/(?P<sid>\d+)/around$', 'reanalyseapp.views.dGetHtmlAround'),		# TEI get html content AROUND INTERVENTION (search results)

	########## 4.Speakers
	(r'^e/(?P<eid>\d+)/s/$', 'reanalyseapp.views.esBrowse'),
	(r'^e/(?P<eid>\d+)/s/(?P<sid>\d+)/$', 'reanalyseapp.views.esShow'),
	(r'^e/(?P<eid>\d+)/ss/make$', 'reanalyseapp.views.makeSpeakerSet'),						# MAKE 		SpeakerSet
	(r'^e/(?P<eid>\d+)/ss/(?P<ssid>\d+)$', 'reanalyseapp.views.getSpeakerSetSpeakers'),		# GET 		SpeakerSet
	(r'^e/(?P<eid>\d+)/ss/delete$', 'reanalyseapp.views.deleteSpeakerSets'),				# DELETE 	SpeakerSets
	(r'^e/(?P<eid>\d+)/setcolor$', 'reanalyseapp.views.setColor'),							# set speaker(s) color
	(r'^e/(?P<eid>\d+)/resetcolor$', 'reanalyseapp.views.resetColors'),						# set all random colors
	
	(r'^e/(?P<eid>\d+)/s/(?P<sid>\d+)/ngrams$', 'reanalyseapp.views.esGetSolrTermVector'),	# useful just to fetch solr ngrams for that speaker
	
	########## 5.Visualizations
	(r'^e/(?P<eid>\d+)/v/$', 'reanalyseapp.views.evBrowse'),
	(r'^e/(?P<eid>\d+)/json/d/(?P<tid>\d+)/$', 'reanalyseapp.views.getLittleFriseJson'),	# little frise texte/speaker content d3 display (for ed/sBrowse)
	
	(r'^e/(?P<eid>\d+)/v/gethtml$', 'reanalyseapp.views.getVizHtml'),						# fetch viz html
	
	(r'^e/(?P<eid>\d+)/v/make$', 'reanalyseapp.views.makeVisualization'),					# MAKE VISUALIZATION
	(r'^e/(?P<eid>\d+)/v/(?P<vid>\d+)/public$', 'reanalyseapp.views.evSetPublic'),			# SWITCH PUBLIC FLAG
	(r'^e/(?P<eid>\d+)/v/(?P<vid>\d+)/delete$', 'reanalyseapp.views.evDelete'),				# DELETE
	(r'^e/(?P<eid>\d+)/v/(?P<vid>\d+)/json$', 'reanalyseapp.views.evGetJson'),				# GET JSON VALUES
	(r'^e/(?P<eid>\d+)/v/(?P<vid>\d+)/save$', 'reanalyseapp.views.evSaveHtml'),				# SAVE HTML of vizu in model (unused?)
	
	(r'^e/(?P<eid>\d+)/v/(?P<vid>\d+)/updatedescr$', 'reanalyseapp.views.evUpdateDescr'),	# AJAX update of the description
	
	########## 6.Search
	(r'^e/(?P<eid>\d+)/search/', 'reanalyseapp.views.eSearch' ),
 	



	################### DEPRECATED
 	#(r'^e/(?P<eid>\d+)/i/(?P<iid>\d+)$', 'reanalyseapp.views.eiGetExtractHtml'),			# Get JSON with html of intervention (for extracts in search results)
 	#(r'^doc/$', 'reanalyseapp.views.docShow'),
 	
# 	# show code
# 	(r'^e/(?P<eid>\d+)/c/(?P<cid>\d+)/$', 'reanalyseapp.views.ecShow'),
# 	# show word
# 	(r'^e/(?P<eid>\d+)/w/(?P<wid>\d+)/$', 'reanalyseapp.views.ewShow'),
# 	# tfidf data in ew_show
# 	(r'^e/(?P<eid>\d+)/json/tfidf/(?P<wid>\d+)$', 'reanalyseapp.views.getWordStat'),
# 	# statenquete in e_browse
# 	(r'^e/(?P<eid>\d+)/json/(?P<data>\w+)/$', 'reanalyseapp.views.getJsonData'),
# 		
# 	(r'^e/(?P<eid>\d+)/action/(?P<cmd>\w+)$', 'reanalyseapp.views.makeAction'),				# ACTION : CAL(calculate TFIDFs) / GET(return jsonTFIDF) / GRAPH(make graph Words/Speakers)
# 	
# 	# styling deprecated ! (made in the parsing)
# 	#(r'^e/(?P<eid>\d+)/d/(?P<did>\d+)/refresh$', 'reanalyseapp.views.edStylizeContent'),	# TEI/CAQDAS : build html content from objects
# 	
# 	#(r'^e/(?P<eid>\d+)/d/(?P<did>\d+)/json$', 'reanalyseapp.views.edGetJson'),				# Get JSON with all Data for D3 - TEXTE
# 	#(r'^e/(?P<eid>\d+)/json$', 'reanalyseapp.views.eGetJson'),								# Get JSON with all Data for D3 - ENQUETE
# 	#(r'^e/(?P<eid>\d+)/tagcloud$', 'reanalyseapp.views.makeTagCloud'),						# Get JSON from GET (form) parameters (TAGCLOUD)
)
