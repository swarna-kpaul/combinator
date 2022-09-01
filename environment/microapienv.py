import requests
from environment.conjugateDriver import *
from environment.dbcred import *
#import util.manageperm as mp
#from util.managemetadata import getadocument, logcalls
#import util.managemetadata as mm
from google.cloud import firestore
from google.cloud.firestore_v1.field_path import FieldPath
#import util.billing as bill
import ast
#import redis
import time
import random
import string
from google.cloud import storage
import google.auth.transport.requests
import google.oauth2.id_token
from urllib.parse import urlparse
from datetime import datetime, timezone
from firebase_admin import auth,initialize_app,get_app,delete_app
import firebase_admin.db as firebasedb
import json
firestoredb = firestore.Client()
storageclient = storage.Client()
inputdatabucket = storageclient.get_bucket(morphisdomIObucket)


try:
	delete_app(get_app())
except:
	pass
firebaseapp = initialize_app(options={"projectId": GOOGLE_CLOUD_PROJECT_USER,'databaseURL':FIREBASERUNNERDBURL})
runnerkeyref = firebasedb.reference('runnerkeys')
#redis_pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASS, max_connections  = 2)
#redis_client = redis.StrictRedis(connection_pool=redis_pool)
##### environment should be an instance of a class

###### mandatory Methods
## reset : None --> None ######### should reset the environment
## get_observation : None --> Any return type ##### get the current observation 
## take_action : Any Input type --> None ######### take action based on input
## get_reward : None --> Number ######### return  normalized total reward between -1 and 1
## check_goalstate : None --> Boolean ########## check if goal is reached
## get_state : None --> dict ###### output current state
import pickle

class microapi:
	def __init__(self,init_state=[],api_map = {},url="https://skpkong.herokuapp.com/"):
		self.state = dict()
		self.state['state'] = pickle.loads(pickle.dumps(init_state,-1))
		self.state['apimap'] = pickle.loads(pickle.dumps(api_map,-1))
		self.state['url'] = pickle.loads(pickle.dumps(url,-1))
		self.init_state = init_state
		self.pending_state = 0
	
	def set_apimap(self,map):
		self.state['apimap'].update(map)
	def set_url(self,url):
		self.state['url'] = pickle.loads(pickle.dumps(url,-1))
	
	def reset (self):
		self.state['state'] = pickle.loads(pickle.dumps(self.init_state,-1))
		self.total_reward = 0
		self.curr_reward = 0
			
	def get_observation(self,remoteserviceheader={}):
		if len(self.state['state']) == 2:
			data =self.state['state'][1]
			self.state['state'] = []
			return (data)
		else:
			return (0)
	
	def checkifdocexists(self,collectioname,documentname):
		doc_ref = firestoredb.collection(collectioname).document(documentname)
		doc = doc_ref.get()
		return doc.exists
	
	def adddocument(self,collectioname, documentdata, documentname=''):
		collc_ref = firestoredb.collection(collectioname)
		if documentname =='':
			collc_ref.document().set(documentdata)
		else:
			collc_ref.document(documentname).set(documentdata)
		
		
	def updatedocument(self,collectioname,documentname,documentdata):
		doc_ref = firestoredb.collection(collectioname).document(documentname)
		doc_ref.update(documentdata)
			
	def logcalls(self,calltype,runid,logdata):
		transid = 'tr'+''.join(random.choices(string.ascii_uppercase + string.digits, k = 8))
		if calltype == 'API':
			collectionname = 'apirequestlog'
		else:
			collectionname = 'graphrequestlog'
		if self.checkifdocexists(collectionname,runid):
			self.updatedocument(collectionname,runid,{transid:logdata})
		else:
			self.adddocument(collectionname,{transid:logdata},runid)
	
	def take_action(self,action,remoteserviceheader={}):
		current_state = self.state['state']
		print("at take action time",current_state, time.time())
		if 1==1:
			########### Take action
			if not current_state:
				apiname = action ###self.state['apimap'][action]
				self.state['state'].append(apiname)
			elif self.state['state'][0] == 'clientcomm':
				clientcommtoken = remoteserviceheader['clientcommtoken']
				userid = remoteserviceheader['userid']
				clientcommand = action
				#try:
				output,status = clientcomm(clientcommtoken,clientcommand,userid)
				#except Exception as e:
				if status == 1:
					#print ("clientcomm exception", str(e))
					self.pending_state = 1
					return
				elif status == 2:
					raise NameError("Argh! It seems that there is an internal error while recieving your data.")
				self.state['state'].append(CheckOutputStream(output))
			elif self.state['state'][0] == 'setattrib':
				clientcommtoken = remoteserviceheader['clientcommtoken']
				#userid = remoteserviceheader['userid']
				runidattribref = runnerkeyref.child(clientcommtoken+'-attrib')
				runidattribref.set(str(action))
				self.state['state'].append(CheckOutputStream(0))
			elif self.state['state'][0] == 'userapigetdata':
				clientcommtoken = remoteserviceheader['clientcommtoken']
				clientparameters = action
				output,status = getapiuserdata(clientcommtoken,clientparameters,remoteserviceheader['userid'])
				if status == 1:
					#print ("clientcomm exception", str(e))
					print(json.dumps({'user':remoteserviceheader['userid'],'clientcommtoken':remoteserviceheader['clientcommtoken'],'operation':'userapigetdata','message':output,'severity' : 'ERROR','sourcecodeexcept':None,'runid':remoteserviceheader['runid']}))
					raise NameError(output)
				self.state['state'].append(CheckOutputStream(output))	
			else:
				###################################### get remote metadata ####################3
				#metadata = mp.getresultfromDB(query = """select hosturl,headers,params from reusablefun where functionname = %s """, inputlist=[self.state['state'][0]])[0]
				print("before fetching url time",current_state, time.time())
				metadata = firestoredb.collection("reusablefun").document(self.state['state'][0]).get().to_dict()#mm.getadocument("reusablefun",self.state['state'][0])
				print("after fetching url time",current_state, time.time())
				#print("ApI: ",self.state['state'][0])
				headers = ast.literal_eval(metadata['headers']) #
				headers.update(remoteserviceheader)
				params = ast.literal_eval(metadata['params'])
				url = metadata['hosturl']  #self.state['url']+self.state['state'][0]
				data = CheckInputStream(action,headers,storageclient,morphisdomworkspacebucket,remoteserviceheader['userid'],remoteserviceheader['runid'])
				######## check if it is internally hosted API
				hostname = urlparse(url).hostname
				if GCP_PROJECT_HOSTEDFUNCTION in hostname or GOOGLE_CLOUD_PROJECT in hostname or GCP_PROJECT_UTILITIES in hostname or hostname.endswith(".run.app"):
					try:
						auth_req = google.auth.transport.requests.Request()
						id_token = google.oauth2.id_token.fetch_id_token(auth_req, url)
						headers['Authorization'] = 'Bearer '+id_token
					except:
						pass
				
				apistarttime = datetime.now(timezone.utc)
				if 'Content-Type' in headers:
					if headers['Content-Type'] == 'application/json':
						#print("json",headers)
						x = requests.post(url, json = data,headers=headers, params = params)
					else:
						x = requests.post(url, data = data,headers=headers, params = params)
				else:
					x = requests.post(url, data = data,headers=headers, params = params)
				apiendtime = datetime.now(timezone.utc)
				###############################
				#print ("status code", x.status_code)	
				
				if x.status_code == 208:
					logdata = {'apiname':self.state['state'][0],'calltime':apistarttime,'endtime':apiendtime,'isdataapi':'N','quantity':1,'runstatus':'usererror','userid':headers['sessionuser']}
					self.logcalls('API',remoteserviceheader['runid'],logdata)
					#bill.logapicall(userid= headers['sessionuser'],apiname= self.state['state'][0],quantity = 1,runid=remoteserviceheader['runid'],starttime=apistarttime,endtime=apiendtime,runstatus = "usererror")
					raise NameError("Sorry! A module called "+self.state['state'][0]+' failed within the morph due to '+x.content.decode('utf-8'))
				elif x.status_code != 200:
					print(x.content.decode('utf-8'))
					logdata = {'apiname':self.state['state'][0],'calltime':apistarttime,'endtime':apiendtime,'isdataapi':'N','quantity':1,'runstatus':'internalerror','userid':headers['sessionuser']}
					self.logcalls('API',remoteserviceheader['runid'],logdata)
					#bill.logapicall(userid= headers['sessionuser'],apiname= self.state['state'][0],quantity = 1,runid=remoteserviceheader['runid'],starttime=apistarttime,endtime=apiendtime,runstatus = "internalerror")
					raise NameError("Argh! A module called "+self.state['state'][0]+' failed within the morph due to '+x.content.decode('utf-8') + ' You will not be charged for this run.')
				else:
					###################### add billing
					print("before logging api call time",current_state, time.time())
					logdata = {'apiname':self.state['state'][0],'calltime':apistarttime,'endtime':apiendtime,'isdataapi':'N','quantity':1,'runstatus':'complete','userid':headers['sessionuser']}
					self.logcalls('API',remoteserviceheader['runid'],logdata)
					print("after logging api call time",current_state, time.time())
					#bill.logapicall(userid= headers['sessionuser'],apiname= self.state['state'][0],quantity = 1,runid=remoteserviceheader['runid'],starttime=apistarttime,endtime=apiendtime,runstatus = "complete")
				#print("content",x.content)
				
				#bill.logapicall(userid = headers['sessionuser'],apiname = self.state['state'][0],quantity=1)
				self.state['state'].append(CheckOutputStream(x.content))
		#except Exception as e:
		#	print("exception",e)
		#	raise NameError("Error in API call "+self.state['state'][0]+' due to '+repr(e))
		#self.total_reward += self.curr_reward
		return 

	def get_reward(self):
		return self.total_reward
		
	def get_state(self):
		return self.state
		
	def set_state(self,state):
		self.state = state
		
	def check_goalstate(self,data,remoteserviceheader={}):
		return False



########### get user data from API

def getapiuserdata(clientcommtoken,clientparameters,userid):
	clientcommtokenref = runnerkeyref.child(clientcommtoken)
	try:
		clientcommtokendata = clientcommtokenref.get()
	except Exception as e:
		print("error in fetchingclientcommtoken")
		time.sleep(1)
		clientcommtokendata = clientcommtokenref.get()
	if not clientcommtokendata:
		time.sleep(1)
		clientcommtokendata = clientcommtokenref.get()
	if clientcommtokendata:
		clientdata = clientcommtokendata
		try:
			clientdata = ast.literal_eval(clientdata)
		except:
			pass
		try:
			clientparameters = ast.literal_eval(clientparameters)
		except:
			pass
		if isinstance(clientparameters,dict): ### only one input parameter
			try:
				clientdata = clientdata[clientparameters['paramname']]
			except Exception as e:
				print(e)
				return "Argh! It seems that there is an internal error while recieving your API data. Incorrect parameters supplied!",1
		elif isinstance(clientparameters,list):
			try:
				clientdata = [clientdata[i['paramname']] for i in clientparameters]
			except Exception as e:
				print(e)
				return "Argh! It seems that there is an internal error while recieving your API data. Incorrect parameters supplied!",1
		else:
			return "Argh! It seems that there is an internal error while recieving your API data. API parameters are incorrectly defined in source. You may not use this API until further notice!",1
		output, status = prepare_output(clientdata,userid)
		clientcommtokenref.delete()
		if status == 1:
			return "Argh! It seems that there is an internal error while recieving your API data. Request timed out while checking uploaded data!",1
		else:
			return output,0
	else:
		return "Argh! It seems that there is an internal error while recieving your API data. Client token not found for uploaded data!",1

################### types of clientcommand
###### uploadfile - request client to upload a file
###### captureimage - request client to capture a image and upload
###### gettext - request client to oppen textbox and upload text
###### getlocation - request client to upload current location
###### getaudio - request client to upload 10 sec audio recording
###### uploadfilemulti - request client to upload multiple files


def check_gcs_filepresence(clientdataitem,userid,getdata=False):
	if str(clientdataitem).startswith('gs://'+morphisdomIObucket):  ####### uploaded file
		for i in range(2):
			if storage.Blob(bucket=inputdatabucket, name=userid+'/input/'+clientdataitem.split('/')[-1]).exists(storageclient): #### check if file exists
				break
			if i == 1:
				return "Request timed out",1
			time.sleep(1)
		if getdata:
			blob = inputdatabucket.blob(userid+'/input/'+clientdataitem.split('/')[-1])
			data = blob.download_as_string()
			blob.delete()
			return data,0
	return clientdataitem,0


def prepare_output(clientdata,userid,returntype='ptr'):
	if isinstance(clientdata, str) :
		#print("client data item non list",clientdata)
		if returntype == 'data':
			getdata = True
		else:
			getdata = False
		data, status = check_gcs_filepresence(clientdata,userid,getdata=getdata)
		#print("gcs",data)
		if status == 1:
			print("error checking file presence", clientdata)
			return data, status
		output = data
	elif isinstance(clientdata, list) : ##### multifile or multicommand
		output=[]
		for clientdataitem in clientdata:
			#print("client data item list",clientdataitem)
			msg, status = check_gcs_filepresence(clientdataitem,userid)
			if status == 1:
				print("error checking file presence",clientdataitem)
				return msg, status
			clientdataitem,status = prepare_output(clientdataitem,userid)
			if status == 1:
				print("error preparing file data",clientdataitem)
				return clientdataitem,status 
			output.append(clientdataitem)	
	else:
		output = clientdata
	return output,0


def clientcomm(clientcommtoken,clientcommand,userid):
	clientcommtokenref = runnerkeyref.child(clientcommtoken)
	try:
		clientcommtokendata = clientcommtokenref.get()
	except Exception as e:
		print("error in fetchingclientcommtoken")
		time.sleep(1)
		clientcommtokendata = clientcommtokenref.get()
	if not clientcommtokendata:
		time.sleep(1)
		clientcommtokendata = clientcommtokenref.get()
	if clientcommtokendata:
	#### graph already ran now restarting from pending state
		command = clientcommtokendata
		commandtoken = command['commandtoken']
		clientcommand = command['clientcommand']
		commandtokenref = runnerkeyref.child(clientcommtoken+commandtoken)
		clientdata = commandtokenref.get()
		try:
			clientdata = ast.literal_eval(clientdata)
		except:
			pass
		if len(clientcommand) <4:
			returntype = 'data'
		elif clientcommand[3] == 'pointer':
			returntype = 'pointer'
		else:
			returntype = 'data'
		print("clientdata",clientdata)
		output, status = prepare_output(clientdata,userid,returntype)
		clientcommtokenref.delete()
		commandtokenref.delete()
		if status == 1:
			return "Request timed out",2
		else:
			return output,0
	else:
		commandtoken = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 16))
		clientcommtokenref.set({'clientcommand':clientcommand, 'commandtoken':commandtoken})
		return "Request timed out",1
	
	
	# for i in range(2):
		# if storage.Blob(bucket=inputdatabucket, name=userid+'/input/'+clientcommtoken+commandtoken).exists(storageclient):
			# if clientcommand[0] == 'uploadfilemulti': ## return pointers to multiple uploaded filez
				# output=[]
				# newstorageclient = storage.Client()
				# for blob in newstorageclient.list_blobs(morphisdomIObucket, prefix=userid+'/input/'+clientcommtoken+commandtoken):
					# output.append('gs://'+morphisdomIObucket+'/'+blob.name)
				# output.remove('gs://'+morphisdomIObucket+'/'+userid+'/input/'+clientcommtoken+commandtoken)
				# redis_client.delete(clientcommtoken)
				# redis_client.delete(clientcommtoken+commandtoken)
				# return output,0
			# elif returntype == 'data':
				# blob = inputdatabucket.blob(userid+'/input/'+clientcommtoken+commandtoken)
				# data = blob.download_as_string()
				# blob.delete()
				# del blob
				# redis_client.delete(clientcommtoken)
				# redis_client.delete(clientcommtoken+commandtoken)
				# return data,0
			# else:
				# redis_client.delete(clientcommtoken)
				# redis_client.delete(clientcommtoken+commandtoken)
				# return 'gs://'+morphisdomIObucket+'/'+userid+'/input/'+clientcommtoken+commandtoken,0
		# time.sleep(0.5)
	# return "Request timed out",1



api_world = microapi()