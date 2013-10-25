# -*- coding: utf-8 -*-
#
#   Import script for .csv files.
#    Note: manifest a strong printaholism.
#
import sys, os, csv, re, traceback
from optparse import OptionParser
import bag.csv2
import xml.etree.ElementTree as ET
import os


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
   
   e = importEnqueteUsingMeta(upPath,enqueterootpath)
   
   print(e)
   
   #if(e != False):
   doFiestaToEnquete(e)
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
           
#
#CheckMetaDocuments
#Check if every file exists in MetaDocuments
#return False with error dictionnary or True
#
def isMetaDocOK(upload_path, enquete_path):
    
    from imexport import importEnqueteUsingMeta
    
    if os.path.exists(enquete_path):
        #mandatoryFields = ['*id','*name','*category','*description','*location','*date']
        print("=========== PARSING META_DOCUMENTS.CSV TO CHECK IF A FILE IS MISSING IF TRUE IMPORT IS CANCELLED")
        ###### Parsing Documents
        doc = csv.DictReader(open(enquete_path+'_meta/meta_documents.csv'),delimiter='\t')
        
        error = False
        error_dict = {}
        
        for counter, row in enumerate(doc):
            if row['*id']!='descr':
                file_location = upload_path+row['*file']
                try:
                    open(file_location)                        
                except IOError, e:
                    if(e.args[0] == 2):#no such file or directory
                        error = True
                        error_dict.update({file_location:e.args[1]})
			print file_location

        if(error is True):
            return {'status':False, 'error_dict':error_dict}
        else:
            return True




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



def exportEnquiry(enquiry_id, enquete_id):
    enquiry = Enquiry.objects.filter(enquiry_id)
    pins = enquiry.pins.all()
    tags = enquiry.tags.all()
    
    #serialize
    

def exportEnquete(enquete_id, filetype):
    
    os.system('rm /var/opt/reanalyse/backup_data/backup_enquete.xml;touch backup_enquete.%s' % filetype)
    
    
    print('enquetes')
    enquetes = Enquete.objects.filter(id=enquete_id)

    enquete = Enquete.objects.get(id=enquete_id)

    
    
    print('enquiries')
    enquiries = Enquiry.objects.filter(enquete = enquete)
    
    
    enquiriesPins = []
    enquiriesTags = []
    for enquiry in enquiries:
        enquiriesPins += enquiry.pins.all()
        enquiriesTags += enquiry.tags.all()
    
    enquiriesPinsGeo = []
    for enquiryPin in enquiriesPins:
        enquiriesPinsGeo += enquiryPin.geos.all()
        
    print('tags')
    tags = enquete.tags.all()
    
    textes = Texte.objects.filter(enquete = enquete)
    
    print('textesTags')
    textesTags = []
    for texte in textes:
        textesTags += texte.tags.all()
    
    
    print('attributes')
    attributeTypes = AttributeType.objects.filter(enquete = enquete)
    attributes = Attribute.objects.filter(enquete = enquete)
    
    print('speakers')
    speakers = Speaker.objects.filter(enquete = enquete)
    
    print('wordEntitySpeakers,speakerTextes,speakerAttributes')
    wordEntitySpeakers = []
    speakerTextes = []
    speakerAttributes = []
    for speaker in speakers:
        speakerTextes += speaker.textes.all()
        wordEntitySpeakers += WordEntitySpeaker.objects.filter(speaker=speaker.id)
        speakerAttributes += speaker.attributes.all()
    
    
    print('wordEntitySpeakerTextes')
    wordEntitySpeakerTextes = []
    for wordEntitySpeaker in wordEntitySpeakers:
        wordEntitySpeakerTextes += wordEntitySpeaker.textes.all()
   
    
    print('speakersets')
    speakerSets = SpeakerSet.objects.filter(enquete = enquete)
    speakerSetSpeakers = []
    for speakerSet in speakerSets:
        speakerSetSpeakers += speakerSet.speakers.all()
        
    
    print('codes')
    codes = Code.objects.filter(enquete = enquete)
    codeTextes = []
    for code in codes:
        codeTextes += code.textes.all()
    
    print('sentence')
    sentence = Sentence.objects.filter(enquete = enquete)
    wordEntities = WordEntity.objects.filter(enquete = enquete)
    wordEntityTextes = []
    for wordEntity in wordEntities:
        wordEntityTextes += wordEntity.textes.all()
    
    
    print('word')
    word = Word.objects.filter(enquete = enquete)
    print('ngram')
    ngram = Ngram.objects.filter(enquete = enquete)
    print('ngramspeaker')
    ngramSpeaker = NgramSpeaker.objects.filter(enquete = enquete)
    
    print('visualizations')
    visualizations = Visualization.objects.filter(enquete = enquete)
    vizTextes = []
    vizSpeakers = []
    for visualization in visualizations:
        vizTextes += visualization.textes.all()
        vizSpeakers += visualization.textes.all()
    
    
    print('create big object')
    
    all_objects = list(tags)
    
    all_objects += list(enquetes)
    
    all_objects +=  list(enquiries)
    all_objects += list(enquiriesPins)
    all_objects += enquiriesPinsGeo

    
    all_objects += list(textes)
    all_objects += list(textesTags)
    
    all_objects += list(codes)
    all_objects += list(codeTextes)
    
    
    all_objects += list(attributes)
    all_objects += list(attributeTypes)
    
    all_objects += list(speakers)
    all_objects += list(speakerTextes)
    all_objects += list(speakerAttributes)
    
    all_objects += list(speakerSets)
    all_objects += list(speakerSetSpeakers)
    
    
    all_objects += list(wordEntities)
    all_objects += list(wordEntityTextes)
    
    all_objects += list(word)
    

    all_objects += list(sentence)
    
    
    all_objects += list(wordEntitySpeakers)
    all_objects += list(wordEntitySpeakerTextes)
    
    
    all_objects += list(visualizations)
    all_objects += list(vizSpeakers)
    all_objects += list(vizTextes)
    
    all_objects += list(ngram)
    all_objects += list(ngramSpeaker)
    
    all_objects += enquiriesPins
    all_objects += enquiriesTags
    
    print('serialize big object')
    data = serializers.serialize('json', all_objects)
    
    
    print('save file')
    with open("backup_enquete.json", "w") as f:
        f.write(data)

    
    
    """
    root = ET.fromstring(data)
    
    api_results = root.findall('.//object')
    
    for object in api_results:
        
        try:
            del object.attrib["pk"]
        except:
            pass
        
    tree = ET.ElementTree(root)
    with open("backup_enquete.xml", "w") as f:
        tree.write(f)
    
    """
    
    print('change location file path')
    os.system('perl -pi -e "s/\/var\/opt\/reanalyse/\/datas\/www\/app/" /var/opt/reanalyse/backup_data/backup_enquete.%s;sed -i "s/\/var\/opt\/reanalyse/\/datas\/www\/app/g" /var/opt/reanalyse/backup_data/backup_enquete.%s' % (filetype, filetype))
    
    
    print('Zip enquete')
    #zip enquete path
    os.system("tar -cvf --no-recursion /var/opt/reanalyse/backup_data/enquete.tar %s " % (enquete.uploadpath))
    


def parseAllTeis(enquete_id):
    
    textes = Texte.objects.filter(enquete_id=enquete_id, doctype="TEI")

    for t in textes :
        
        if not t.id == 14825:
            parseXmlDocument(t)
    
    
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
