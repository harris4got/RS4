import urllib.request, urllib.parse, urllib.error, re, html, webbrowser, hashlib, os
from re import search
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk

LOC=os.environ.get('HOME')+'/.local/share/rhythmbox/plugins/RS4/'
SESSION_FILE=LOC+'.session'
THE_API_FILE=LOC+'.api'
FILE={'session':SESSION_FILE}

def get_api(option):
	try:
		stream=open(THE_API_FILE,"r")
		if option==0:
			API_KEY=search('API_KEY=(.+)',stream.read()).group(1)
			stream.close();return(API_KEY)
		if option==1:
			API_AD=search('API_AD=(.+)',stream.read()).group(1)
			stream.close();return(API_AD)
	except:
		print("API details could not be found")
		return None

DEF_CAB={'artist':'<artist>(.+)</artist>','title':'<title>(.+)</title>','duration':'<duration>(\d+)</duration>','album':'<album>(.+)</album>'}
API_URL = 'http://ws.audioscrobbler.com/2.0/'
API_KEY = get_api(0)
API_AD = get_api(1)
DIRS=dir();exec('p0='+DIRS[0]);exec('p1='+DIRS[1])


def record(string,method):				#Logging/Archiving
	log=open(FILE[method],"a+")
	log.writelines(string)
	log.close()

def xmllight(string,cab=DEF_CAB):			#Indigenous XML Parser
	for x in cab:
		t=search(str(cab[x]),str(string))
		if t:
			cab[x]=t.group(1)
			if '&' in str(cab[x]):
				cab[x]=html.unescape(str(cab[x]))
		else:
			cab[x]=None	

def process(code):					#String Processing
	output=""
	i=0
	while i<code.count('')-1:
		if code[i]=="1":
			output+=chr(int(code[i:i+3]))
			i+=3
		else:
			output+=chr(int(code[i:i+2]))
			i+=2
	return output	


def get_session():					#Get Session Key
	try:
		stream=open(SESSION_FILE,"r")
		sk=search('session_key=(.+)',stream.read()).group(1)
		stream.close()
	except:
		p3=process(p1);exec('global '+DIRS[1]+";"+DIRS[1]+"=p3")
		parameters={'api_key':API_KEY,'method':"auth.getToken"}
		param=get_sig(parameters)
		doc=get_doc(param)
		if not doc:
			return None
		cab={'token':'<token>(.+)</token>'}
		xmllight(doc,cab)
		if not cab['token']:
			print("Error getting token from Last FM")
			return None
		authurl='http://www.last.fm/api/auth/?api_key=%s&token=%s'%(API_KEY,str(cab['token']))
		print(authurl)
		try:
			webbrowser.open(authurl,new=2,autoraise=True)
		except:
			print("Error opening the auth url")
			return None
		dialog = gtk.Dialog("Acceptance", None, 0,(gtk.STOCK_OK, gtk.ResponseType.OK))
		label=gtk.Label("After you grant permission in browser, click OK")
		label.show()
		dialog.get_content_area().add(label)
		response = dialog.run()
		dialog.destroy()
		while gtk.events_pending():
			gtk.main_iteration()
		if response == gtk.ResponseType.OK:
			print ("Accepted")
		else:
			return None
		parameters = { "method" : "auth.getsession", "api_key": API_KEY, "token":str(cab['token']) }
		param=get_sig(parameters)
		doc=get_doc(param)
		if not doc:
			print("Couldn't get session key from Last FM: Did you click on 'Yes, allow Access'?")
			return None
		cab={'name':'<name>(.+)</name>','sk':'<key>(.+)</key>','subscriber':'<subscriber>(\d)</subscriber>'}
		xmllight(doc,cab)
		string="[radioscrobbler]\nuser=%s\nsubscriber=%s\nsession_key=%s"%(cab['name'],cab['subscriber'],cab['sk'])
		record(string,'session')
		sk=cab['sk']
	return sk

def get_sig(parameters):				#API Authentication Parameter Builder
		md5 = hashlib.md5()
		p2=process(p0);exec('global '+DIRS[0]+";"+DIRS[0]+"=p2")
		keys = sorted(parameters.keys())
		keyvalues = []
		for key in keys:
				keyvalues.append(str(key))										
				keyvalues.append(str(parameters[key]))

		sig = ''.join(keyvalues)
		sig = sig + API_AD
		try:
			sig=sig.encode('utf-8')
		except UnicodeDecodeError:
			print("Unicode Decode Error")	
		md5.update(sig)
		api_sig = md5.hexdigest()
		parameters["api_sig"] = api_sig
		return parameters

def get_doc(parameters):				#API Response Reader	 
		data=urllib.parse.urlencode(parameters)
		url="%s?%s"%(API_URL,data)
		try:
			return urllib.request.urlopen(url).read()
		except:
			print("Sorry, couldn't read a valid response from Last FM")
			return None




