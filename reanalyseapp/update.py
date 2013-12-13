# -*- coding: utf-8 -*-
#
#   Import script for .csv files.
#    Note: manifest a strong printaholism.
#
import sys, os, csv, re, traceback
from optparse import OptionParser
import bag.csv2
import xml.etree.ElementTree as ET
import os,re,mimetypes
from django.conf import settings as django_settings

from django.template.defaultfilters import slugify


# get path of the django project
path = ("/").join( sys.path[0].split("/")[:-1] )
ppath = ("/").join( sys.path[0].split("/")[:-2] )

if path not in sys.path:
    sys.path.append(path)
if ppath not in sys.path:
    sys.path.append(ppath)
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.core import serializers
from django.core.files import File

# django specific import
from django.conf import settings
from outside.models import VizControl, Enquiry
from datetime import datetime

from reanalyseapp.views import *

from reanalyseapp.models import *

from glue.models import Pin


def update( textes, enquete, csvdict ):

    print "        %s documents found in enquete: \"%s\", id:%s" % ( textes.count(), enquete.name, enquete.id )
    print
    
    
    #Create vizControl entry
    
    try:
        t = VizControl.objects.get( enquete=enquete )
    except VizControl.DoesNotExist, e:
        print  "            creating vizControl..."
        viz = VizControl( enquete=enquete, timeline=True, classement=True, map=True )
        viz.save()
    
   
    
    
    for (counter, row) in enumerate(csvdict):
        
        
        if counter == 0:
            print "        keys: %s" % row.keys()
            # normally, the second meta_documents csv file line is a field description header.
            continue
        print "        %s." % counter
        
       
        try:
            texte_url = row['file']
            texte_name = row['name']
            locationgeo = re.sub( r'[^0-9\.,-]', '', row['locationgeo'])
            

            
            #researcher = row['*researcher']
            article =  row['article']
            
            if('/' in row['date']):
                sep = "/"
            elif('_' in row['date']) :
                sep = "_"
            elif('-' in row['date']) :
                sep = "-"
            
            if('00' in row['date']):
                dateFormat = '%y'
                #row['date'] = row['date'].replace('00', '').replace(sep, '')
                
                print(row['date'])
            else:
                dateFormat = '%d'+sep+'%m'+sep+'%y'
            
            
            
            #print(row['*date'])
            date = row['date'].replace(sep, '-')#datetime.datetime.strptime(row['*date'], dateFormat) #"31-12-12"
            
            #date = datetime.datetime.strptime(row['*date'], '%d/%m/%y').strftime(dateFormat)       
           
        except KeyError, e:
            print "            Field format is not valid: %s " % ( e )
            break

        # print row['*name']doc_name =             row['*name']
        
        try:
            texte = Texte.objects.get( enquete=enquete, name=row['name'], locationpath__regex=( ".?%s" % os.path.basename( texte_url ) ) )

        except Texte.DoesNotExist, e:
            print "            No texte found with : \"%s\", %s " % ( texte_name, e )
            
            foo=raw_input('\n            Skip this line and go on ? [ Y / N ] : ')
            
            if foo.upper() == 'N':
                print "            Script stopped !"
                break
            continue
        except Texte.MultipleObjectsReturned, e:
            print "            More than one texte found with : \"%s\", %s, %s " % ( texte_name, os.path.basename( texte_url ), e )
            foo=raw_input('\n            Skip this line and go on ? [ Y / N ] : ')
            
            if foo.upper() == 'N':
                print "            Script stopped !"
                break
            
        print "            %s \"%s\": %s" % ( texte.id, texte_name, locationgeo )
        
        # get or save tag
        print  "            %s \"%s\": %s" % ( texte.id, texte_name, article )

        try:
            t = Tag.objects.get( type=Tag.ARTICLE, slug=article )
        except Tag.DoesNotExist, e:
            print  "            %s \"%s\": creating tag [%s:%s]" % ( texte.id, texte_name, article, Tag.ARTICLE )
            t = Tag( type=Tag.ARTICLE, slug=article, name=article)
            t.save()

        # save location geo
        texte.locationgeo = locationgeo
        texte.tags.add( t )
        texte.date = date
        texte.save()
        #try


def install( upload_path, enquete_path ) :
    from imexport import importEnqueteUsingMeta
    print "        from upload path '%s'" % upload_path
    
    if not os.path.exists( upload_path ):
        print "        upload_path folder '%s' does not exists or it is not readable !" % upload_path
        print
        return
    
    print "        from upload path '%s'" % enquete_path
    if not os.path.exists( enquete_path ):
        print "        enquete_path folder '%s' does not exists or it is not readable !" % enquete_path
        print
        return

    print "        call importEnqueteUsingMeta (please follow up in log file)"
    importEnqueteUsingMeta( upload_path, enquete_path )
    print "        installation completed."





def testTEIparse(texte_id):
    
    ids = texte_id.split(",")
    
    print(ids)
    
    exit
    
    
    for id in ids:

        texte = Texte.objects.get(id=id)
        try:
            texte.parseXml()
        except Exception, e:
            print(e)
            print "Exception in user code:"
            print '-'*60
            traceback.print_exc(file=sys.stdout)
            print '-'*60
    

def testEnqueteImport(foldName):
    folname = foldName    
    upPath = settings.REANALYSEUPLOADPATH+folname+"/"
    enqueterootpath='' 
    
    for f in os.listdir(upPath+"extracted/"):
        if os.path.exists(upPath+"extracted/"+f+"/_meta/"):
            enqueterootpath = upPath+"extracted/"+f+"/"
   
   
    if isMetaDocOK(enqueterootpath):
       e = importEnqueteUsingMeta(upPath,enqueterootpath)
       doFiestaToEnquete(e)
    
    else:
        exit()

   

   
   #if(e != False):
   
   #else:
    #    exit()


def deleteSpeakers(enquete_id):
  
   
    textes = Texte.objects.filter(enquete_id=enquete_id, doctype="TEI")

    for t in textes :
        speakers = t.speaker_set.filter()
        
        print(speakers)
        for s in speakers :
            s.delete()
            



def reloadSpeakers(enquete_id, spkPath):
    
    enquete = Enquete.objects.get(id=enquete_id )
    print(spkPath)
    if os.path.exists(spkPath):
        print("=========== PARSING META_SPEAKERS.CSV")            
        ###### Parsing Speakers
        spk = bag.csv2.UnicodeDictReader(open(spkPath),delimiter=getCsvDelimiter(spkPath),quotechar='"')
        headers = spk.fieldnames
        mandatories = ["*pseudo","*id","*type"]
        attributetypes=[]
        
        
        
        for catval in headers:
            if catval not in mandatories: # we create only "un-mandatory" attributetypes, since mandatories are stored in speaker model structure
                if catval.startswith("_") or catval.startswith("*"):
                    publicy = '0'
                else:
                    publicy = '1'
        
                newAttType,isnew = AttributeType.objects.get_or_create(enquete=enquete,publicy=publicy,name=catval)
                attributetypes.append(newAttType)
        
        for row in spk:
        
            #try:
            if row['id']!='descr':
                spk_id =     row['id']
                spk_type =     SPEAKER_TYPE_CSV_DICT.get(row['type'],'OTH')
                spk_name =     row['pseudo']
        
                #verify if the speaker exists
                
                
                
                newSpeaker,isnew = Speaker.objects.get_or_create(enquete=enquete,ddi_id=spk_id,ddi_type=spk_type,name=spk_name)
                
                
                
                newSpeaker.public = (spk_type=='SPK' or spk_type=='PRO')
    
                for attype in attributetypes:
                    
                    attval=row[attype.name]
                    if attval=='':
                        attval='[NC]'
                        newAttribute,isnew = Attribute.objects.get_or_create(enquete=enquete,attributetype=attype,name=attval)
                        newSpeaker.attributes.add(newAttribute)
               
                try:
                   newSpeaker.save()
                except Exception, error:
                    print "An exception was thrown!"
                    print str(error)
    else:
        print("=========== PARSING: no spk meta found")
           


def commit_enquete( enquete_id ):
    
    #create dump of prod bdd
    os.system('pg_dump -C -h 10.36.1.15 -U app app | psql -h localhost -U reanalyse reanalyse > prod_db.dump')
    
    #create dump of dev bdd
    os.system('pg_dump -Ft -b reanalyse > dev_db.dump')
    
    
    #Create update sql file for production
    os.system('apgdiff prod_db.dump dev_db.dump > diff.sql')
    
    #change absolute path (/var/opt/reanalyse to /datas/www/app
    
    #transfert



def main( argv ):
    print """
        
    WELCOME TO APP UPDATER

    -------------------------------

    """
    parser = OptionParser( usage="\n\n%prog --enquete=34 --csv=/home/dgu/meta_documents.csv" )

    parser.add_option("-c", "--csv", dest="csvfile", help="csv file absolute path", default="" )
    parser.add_option("-e", "--enquete", dest="enquete_id", help="enquete identifier", default=0 )
    parser.add_option("-p", "--upload_path", dest="upload_path", help="enquete upload path", default="" ) #use with --func=install
    parser.add_option("-x", "--enquete_path", dest="enquete_path", help="enquete extracted path", default="" ) #use with --func=install
    parser.add_option("-f", "--function", dest="func", help="update function", default="update" )
    parser.add_option("-d", "--document_id", dest="document_id", help="document id (Texte)", default="" )
    parser.add_option("-D", "--directory", dest="directory", help="upload directory study", default="" )
    parser.add_option("-F", "--filetype", dest="filetype", help="filetype for backup data file (xml, json, yaml)", default="json" )

    ( options, argv ) = parser.parse_args()

    if options.func == "isMetaDocOK" :
        print(options.func)
        # install the enquete
        return isMetaDocOK( options.upload_path, options.enquete_path )

    if options.func == "install" :
        if options.csvfile is None:
            error("csvfile arg was not found!", parser)
        else:
            # install the enquete
            return install( options.upload_path, options.enquete_path )
        
    if options.func == "testTEIparse" :
        print(options.func)
        # install the enquete
        return testTEIparse( options.document_id )
    
    
    if options.func == "testDownload" :
        print(options.func)
        # install the enquete
        return testDownload( options.enquete_id )
    
    if options.func == "testEnqueteImport" :
        print(options.func)
        # install the enquete
        return testEnqueteImport( options.directory )

    if options.func == "parseAllTeis" :
       print(options.func)
       # reparseAllteis file of an enquete
       return parseAllTeis( options.enquete_id )

    
    if options.func == "exportEnquete" :
       print(options.func)
       # reparseAllteis file of an enquete
       return exportEnquete( options.enquete_id, options.filetype )
    
    
    if options.func == "reloadSpeakers" :
        print(options.enquete_id)
        return reloadSpeakers( options.enquete_id, options.csvfile )
    
    
    if options.func == "deleteSpeakers" :
        print(options.func)
        # reparseAllteis file of an enquete
        return deleteSpeakers( options.enquete_id )
    
    if options.func == "deserialize_data" :
        print(options.func)
        # reparseAllteis file of an enquete
        return deserialize_data( options.csvfile )
    
    if options.func == "importEnqueteSurEnquete" :
        print(options.func)
        # reparseAllteis file of an enquete
        return importEnqueteSurEnquete( options.csvfile, options.enquete_id )
    

    if options.enquete_id is None:
        error("enquete_id arg not found!", parser)

    
   

    if not os.path.exists( options.csvfile ):
        error( message="csv file was not found.", parser=parser )

    try:
        enquete = Enquete.objects.get( id=options.enquete_id )
        textes = Texte.objects.filter( enquete=enquete )
    except Enquete.DoesNotExist, e:
        error("noo %s" % e, parser )

    if textes.count() == 0:
        error("no Texte is attached ...? Is that possible ?", parser )

    # parse csv file !

    csvdict = bag.csv2.UnicodeDictReader(open(options.csvfile, 'rb'), delimiter=';',
                            encoding='utf-8')
    
    for t in textes:
       pass# print(textes.count())#print t.name #, t.locationpath
    update( textes, enquete, csvdict )

    print """

    -------------------------------

    THANK YOU FOR USING APP UPDATER
    Task completed. Bye!

    """



def importEnqueteSurEnquete(eseXmlPath, enquete_id):
   
    e = Enquete.objects.get(id=enquete_id)
    
    tree = etree.parse(eseXmlPath)
    root = tree.getroot()
    
    baseEseXmlFolder = '/'.join(eseXmlPath.split('/')[:-1])+'/'
    
    
    fileName = os.path.basename(os.path.normpath(eseXmlPath))
    folderName = os.path.basename(os.path.normpath(baseEseXmlFolder))
    
    
    out = {}
    out['audiopaths'] = {}
    apacount = 0
    
    
    for lan in ['fr','en']:
        res = {}
        
        # Fetching report
        rep = root.findall('Report')[0]
        res['reportpath'] = baseEseXmlFolder + rep.find('file[@lang="'+lan+'"]').attrib['location']
        
        
        #Create the inquiry
        
        slug = slugify( root.find('./title[@lang="'+lan+'"]').text)
        title = root.find('./title[@lang="'+lan+'"]').text
        content = root.find('./content[@lang="'+lan+'"]').text
        
        authors = root.findall('./authors/author')
        

        try:
            
            enquiry = Enquiry.objects.get(enquete=e,language=lan.upper())
            
        except Enquiry.DoesNotExist:
            enquiry = Enquiry.objects.create(slug=slug, 
                                  title=title, 
                                  content=content, 
                                  language=lan.upper(), 
                                  enquete=e)
                                  
        
        
        
        place = root.find('./interview/place[@lang="'+lan+'"]').text
        date = root.find('./interview/date[@lang="'+lan+'"]').text
        researcher = root.find('./interview/researcher').text
        
        #Ajouter les TAGS
        for author in authors:
            try:
                tag = Tag.objects.get(type="AU", name=author.text)
                enquiry.tags.add(tag)
            except Tag.DoesNotExist, e:
                tag = Tag.objects.create(type="AU", name=author.text,slug=author.text)
                
        
        try:
            tag = Tag.objects.get(type="Pl", name=place)
            enquiry.tags.add(tag)
        except Tag.DoesNotExist, e:
            tag = Tag.objects.create(type="Pl", name=place, slug=place)
            
        
        try:
            tag = Tag.objects.get(type="Da", name=date, slug=date)
            enquiry.tags.add(tag)
        except Tag.DoesNotExist, e:
            tag = Tag.objects.create(type="Da", name=date, slug=date)
        
        
        try:
            tag = Tag.objects.get(type="Rs", name=researcher, slug=researcher)
            enquiry.tags.add(tag)
        except Tag.DoesNotExist, e:
            tag = Tag.objects.create(type="Rs", name=researcher, slug=researcher)
        
                           
        # Fetching chapters
        thechapters = []
        for chapter in root.findall('Chapters/Chapter'):
            chapt = {}
            chapt['name'] = chapter.find('./title[@lang="'+lan+'"]').text
            chapt['html'] = chapter.find('./text[@lang="'+lan+'"]').text
            
            #create pins for the chapter
            
            try:
                chapter_pin = Pin.objects.get(title=chapt['name'], slug=slugify( chapt['name']))
                
            except Pin.DoesNotExist:
            
                chapter_pin = Pin.objects.create( title=chapt['name'],
                           abstract=chapter.find('./abstract[@lang="'+lan+'"]').text,
                           language=lan.upper(), 
                           slug=slugify( chapt['name'] ), 
                           mimetype='',
                           content=chapt['html'],
                           local='' 
                           )
            
            enquiry.pins.add( chapter_pin )
            enquiry.save()
            
            
            thesubchapters = []
            for subChapter in chapter.findall('SubChapter'):
                #try:
                subchapt = {}
                aud = subChapter.find('audio[@lang="'+lan+'"]')
                subchapt['name']         = aud.attrib['name']
                subchapt['audiopath']     = aud.attrib['location']
                location = aud.attrib['location']
                
                patharchive = baseEseXmlFolder+subchapt['audiopath']              
                
                
                if os.path.exists( patharchive ):
                    subchapt['audiopath'] = patharchive
                else:
                    pathserver = settings.REANALYSEESE_FILES+'/'+e.ddi_id+'/'+ subchapt['audiopath']
                    if os.path.exists( pathserver ):
                        subchapt['audiopath'] = pathserver
                    else:
                        logger.info("["+str(e.id)+"] EXCEPT no audio file: "+patharchive)
                        logger.info("["+str(e.id)+"] EXCEPT no audio file: "+pathserver)
                    
                # rather store an id referencing real path in out['audiopaths']
                out['audiopaths'][str(apacount)] = subchapt['audiopath']
                subchapt['audioid'] = str(apacount)
                apacount+=1
                thesubchapters.append(subchapt)
                
                pin_mimetype = mimetypes.guess_type( subchapt['audiopath'])[0]
                
                
                try:
                    sub_pin = Pin.objects.get(title=subchapt['name'], slug=slugify( subchapt['name']))
                    print(sub_pin)
                except Pin.DoesNotExist:
                      #create audio subPins
                    sub_pin = Pin.objects.create( title=subchapt['name'],
                           abstract="",
                           language=lan.upper(), 
                           slug=slugify( subchapt['name'] ), 
                           mimetype=pin_mimetype,
                           content="",
                           local=django_settings.MEDIA_URL+'bequali_ese_files/'+folderName+'/'+os.path.normpath(location),
                           parent=chapter_pin
                           )
                
                
            chapt['subchapters'] = thesubchapters
            thechapters.append(chapt)
        res['chapters'] = thechapters
        out[lan] = res
        
        
        
    return out
    
    pass






def parseAllTeis(enquete_id):
    
    textes = Texte.objects.filter(enquete_id=enquete_id, doctype="TEI")

    for t in textes :
        
        if not t.id == 14825:
            parseXmlDocument(t)


def deserialize_data(file):
    
    #print open(file).read().encode('utf-8')
    
    for deserialized_object in serializers.deserialize("xml", open(file).read().encode('utf-8')):
        print(deserialized_object)
        
        """
        if object_should_be_saved(deserialized_object):
            try:
                deserialized_object.save()
            except Exception, e:
                print(e)
        """
def testDownload(enquete_id):
    import zipfile, zlib
    
    """
    zippath = os.path.join( "/tmp/", "enquete_%s.zip" % enquete_id )

    zf = zipfile.ZipFile( zippath, mode='w' )
    
    
    
    """ 
    for t in Texte.objects.filter( enquete_id=enquete_id ):
        
        if('é'.decode('utf-8') in t.locationpath):
            
            t.locationpath= t.locationpath.replace('é'.decode('utf-8'), 'e')
           
        if os.path.isfile(t.locationpath.decode('utf-8')):
            
            if( t.locationpath.find('_ol') or t.locationpath.find('_dl') ):
                print(t.locationpath.split('/', 7)[7])
               
                """
                zf.write( t.locationpath, compress_type=zipfile.ZIP_DEFLATED, 
                            arcname= t.locationpath.split('/', 5)[5])"""
                            

def error( message="generic error", parser=None):
    print 
    print "   ",message
    print
    print
    if parser is not None:
        parser.print_help()
    exit(-1)


# execute srcipt
if __name__ == '__main__':
    main(sys.argv[1:])
