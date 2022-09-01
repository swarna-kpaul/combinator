import pickle
from google.cloud import firestore
import random
import string
from datetime import datetime,timedelta
import time
from google.cloud.firestore_v1.field_path import FieldPath

db = firestore.Client()

def adddocument(collectioname, documentdata, documentname=''):
	collc_ref = db.collection(collectioname)
	if documentname =='':
		collc_ref.document().set(documentdata)
	else:
		collc_ref.document(documentname).set(documentdata)
		
		
def updatedocument(collectioname,documentname,documentdata):
	doc_ref = db.collection(collectioname).document(documentname)
	doc_ref.update(documentdata)
	
	
def deletedocument(collectioname,documentname):
	db.collection(collectioname).document(documentname).delete()
	
def deletedocfield(collectioname,documentname,fieldname):
	doc_ref = db.collection(collectioname).document(documentname)
	doc_ref.update({fieldname: firestore.DELETE_FIELD})
	

def getalldocuments(collectioname):
	return db.collection(collectioname).stream()


def getadocument(collectioname,documentname):
	doc_ref = db.collection(collectioname).document(documentname)
	doc = doc_ref.get()
	if doc.exists:
		return doc.to_dict()
	else:
		return {}
	
def checkifdocexists(collectioname,documentname):
	doc_ref = db.collection(collectioname).document(documentname)
	doc = doc_ref.get()
	return doc.exists
	
def incrementfield(collectioname,documentname,fieldname,value):
	doc_ref = db.collection(collectioname).document(documentname)
	doc = doc_ref.get()
	if doc.exists:
		doc_ref.update({fieldname: firestore.Increment(value)})
	else:
		doc_ref.set({fieldname:value})

######################################## derivative functions #####################################################################

def logcalls(calltype,runid,logdata):
	transid = 'tr'+''.join(random.choices(string.ascii_uppercase + string.digits, k = 8))
	if calltype == 'API':
		collectionname = 'apirequestlog'
	else:
		collectionname = 'graphrequestlog'
	if checkifdocexists(collectionname,runid):
		updatedocument(collectionname,runid,{transid:logdata})
	else:
		adddocument(collectionname,{transid:logdata},runid)
			
def addtransactions(userid,transdata,runid=None):
	
	if runid == None:
		runid = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 8))
	docref = db.collection('user_transactions_current').document(userid).collection('transactions').document(runid)
	basetransactiondata = {'credit': None,'creditnote': None,'discount': None,'graphname': None,'orderid': None,'runcost': None,'rundate': datetime.now(),'runstatus': None,'runtime': None,'transactiontype':None,'displaygraphname':None}
	if transdata:
		basetransactiondata.update(transdata)
		docref.set(basetransactiondata)
		creditbalance = float(basetransactiondata['credit'] or 0.0) - float(basetransactiondata['runcost'] or 0.0) + float(basetransactiondata['discount'] or 0.0)
		incrementfield("usercreditbalance",userid,"creditleft",creditbalance)
	else:
		transdata = calculateexpense(runid,userid)
		if transdata:
			basetransactiondata.update(transdata)
			if basetransactiondata['runstatus'] in ['complete','killed']:
				creditbalance = float(basetransactiondata['credit'] or 0.0) - float(basetransactiondata['runcost'] or 0.0) + float(basetransactiondata['discount'] or 0.0)
				incrementfield("usercreditbalance",userid,"creditleft",creditbalance)
				adddocument("graphusagelog",{'graphname':basetransactiondata['graphname'],'usagedate':datetime.now(),'userid':userid,'runstatus':basetransactiondata['runstatus']},runid)
			else:
				basetransactiondata['runcost'] = 0
				basetransactiondata['discount'] = 0
			docref.set(basetransactiondata)
	
	
	
def checkpermission(userid,object,permission=['read']):
	############# check adminusers ########################
	if checkifdocexists('adminusers',userid):
		return True
	############# check public permission #################
	publicperm = getadocument('publicpermission',object)
	inferedperm = [k for k,v in publicperm.items() if k in permission and v == 'Y']
	if len(permission) == len(inferedperm):
		return True
	############## check group permission ################
	
	
	############## check user permission ################
	publicperm = getadocument('userpermission',userid+object)
	inferedperm = [k for k,v in publicperm.items() if k in permission and v == 'Y']
	if len(permission) == len(inferedperm):
		return True
	return False

	
def fetchgraphfromDB(graphname):
	graph = getadocument('graphstore',graphname)['graph']
	return pickle.loads(graph)
	
	
	
def calculateexpense(runid,userid):
	######## calculate api cost
	apicalls = getadocument('apirequestlog',runid)
	totalapicost = 0
	totaldiscount = 0
	userdiscount = getadocument('discountrules',userid)
	apinames = {}
	for k,apicall in apicalls.items():
		if apicall['runstatus'] == 'complete' and apicall['apiname'] in apinames:
			apinames[apicall['apiname']] += apicall['quantity']
		else:
			apinames[apicall['apiname']] = apicall['quantity']  
	print(list(apinames.keys()))
	if apinames:
		userapinames = [ userid+i for i in apinames.keys()]
		apinamebillingids = [db.document('apibillingrate/'+i) for i in list(apinames.keys())]
		apinamediscountids = [db.document('discountrules/'+i) for i in list(apinames.keys())]
		userapinamediscountids = [db.document('discountrules/'+i) for i in userapinames]
		apibillingrates = db.collection('apibillingrate').where(FieldPath.document_id(), "in",apinamebillingids ).stream()
		apidiscounts = db.collection('discountrules').where(FieldPath.document_id(), "in", apinamediscountids).stream()
		userapidiscounts = db.collection('discountrules').where(FieldPath.document_id(), "in", userapinamediscountids).stream()
		apicosts = {}
		for doc in apibillingrates:
			apicosts[doc.id] = apinames[doc.id]*doc.to_dict()['rate']
		apidiscounts = {}
		for doc in userapidiscounts:
			apidiscounts[doc.id.replace(userid,'')] = doc.to_dict()['discountrate']
		for doc in apidiscounts:
			if doc.id in apidiscounts:
				continue
			else:
				apidiscounts[doc.id] = doc.to_dict()['discountrate']
		
		for k,v in apicosts.items():
			if k in apidiscounts:
				totaldiscount += apidiscounts[k]*v
			elif userdiscount:
				totaldiscount += userdiscount['discountrate']*v
			totalapicost += v
	
	######## calculate graphcost
	graphcalls = getadocument('graphrequestlog',runid)
	starttimes = []
	elapsetimes = []
	graphcost = 0
	for k,graphcall in graphcalls.items():
		starttimes.append(graphcall['calltime'])
		timdiff = graphcall['endtime']-graphcall['calltime']
		elapsetimes.append(timdiff.total_seconds())
		if graphcall['runstatus'] not in ['pending','running']:
			graphcost = getadocument('graphbillingrate',graphcall['graphname'])['rate']
			userid = graphcall['userid']
			graphname = graphcall['graphname']
			runstatus = graphcall['runstatus']
			graphdiscount = getadocument('discountrules',graphcall['graphname'])
			displaygraphname = getadocument('graphstore',graphcall['graphname'])['displaygraphname']
			usergraphdiscount = getadocument('discountrules',userid+graphcall['graphname'])
			if usergraphdiscount:
				totaldiscount += min(graphcost*usergraphdiscount['discountrate'],graphcost)
			elif graphdiscount:
				totaldiscount += min(graphcost*graphdiscount['discountrate'],graphcost)
			elif userdiscount:
				totaldiscount += min(graphcost*userdiscount['discountrate'],graphcost)
				
	starttime = min(starttimes)
	elapsetime = sum(elapsetimes)
	if graphcost > 0:
		return {'userid':userid,'graphname':graphname,'rundate':starttime,'runtime':elapsetime,'runstatus':runstatus,'runcost':graphcost+totalapicost,'discount':totaldiscount,'transactiontype':'debit','displaygraphname':displaygraphname}
	else:
		return False
	
	
	