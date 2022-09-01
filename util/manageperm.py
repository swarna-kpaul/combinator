from environment.dbcred import *
from psycopg2 import connect
import pickle 

def fetchgraphfromDB(graphname):
	try:
		connection = connect(user = dbuser,password = dbpassword, host = dbhost,port = dbport,database = db)
		cur = connection.cursor()
		cur.execute("select graphname,graph from graphstore where graphname = %s;", [str(graphname)])
		graphname, graph = cur.fetchall()[0]
		graph = pickle.loads(graph)
		cur.close()
		connection.close()
	except Exception as e:
		raise NameError('Unable fetch graph '+graphname+' from DB due to :'+ repr(e))
	return graph

def getresultfromDB(query,inputlist,output_req=True):
	connection = connect(user = dbuser,password = dbpassword, host = dbhost,port = dbport,database = db)
	cur = connection.cursor()
	try:
		cur.execute(query,inputlist)
		if output_req:
			output = cur.fetchall()
		else:
			output = True
		cur.close()
		connection.close()
		return output
			
	except Exception as e:
		cur.close()
		connection.close()	
		raise NameError("query execution failed: "+str(e).replace(":", " "))

def checkobjectpresence(objectname):
	connection = connect(user = dbuser,password = dbpassword, host = dbhost,port = dbport,database = db)
	cur = connection.cursor()
	try:
		cur.execute("select count(1) from graphstore where graphname = %s ",[objectname])
		if cur.fetchall()[0][0] >0:
			cur.close()
			connection.close()
			return True
			
	except Exception as e:
		cur.close()
		connection.close()	
		raise NameError("Create owner permission failed for object "+objectname+" due to "+str(e))
	cur.close()
	connection.close()	
	return False

def create_owner_permission(objectname):
	connection = connect(user = dbuser,password = dbpassword, host = dbhost,port = dbport,database = db)
	cur = connection.cursor()
	try:
		cur.execute("Insert into userpermission(userid,graphid,cangrant,read,write,exe) select ownername,graphid,'Y','Y','Y','Y' from graphstore where graphname = %s ",[objectname])
	except Exception as e:
		cur.close()
		connection.close()	
		raise NameError("Create owner permission failed for object "+objectname+" due to "+str(e))
	cur.execute("commit")
	cur.close()
	connection.close()	

def checkusergrant(grantinguser,objectname,permission=['N','N','N']):
	connection = connect(user = dbuser,password = dbpassword, host = dbhost,port = dbport,database = db)
	cur = connection.cursor()
	########## check admin privileges
	try:
		cur.execute("select count(1) from adminusers where userid = %s",[grantinguser])
		isexistadmin = cur.fetchall()[0][0]
	except Exception as e:
		cur.close()
		connection.close()	
		raise NameError("Fetch permission failed for object "+objectname+" for user "+grantinguser+" due to "+str(e).replace(':','-'))
	if isexistadmin > 0:
		return True
	##########check owner
	try:
		cur.execute("select count(1) from graphstore where ownername = %s and graphname = %s",[grantinguser,objectname])
		isexistowner = cur.fetchall()[0][0]
	except Exception as e:
		cur.close()
		connection.close()	
		raise NameError("Fetch permission failed for object "+objectname+" for user "+grantinguser+" due to "+str(e).replace(':','-'))
	if isexistowner > 0:
		return True
	
	try:
		usercangrant = 'N'; groupcangrant='N'
		cur.execute("select cangrant,read,write,exe from userpermission a join graphstore b on a.graphid = b.graphid and b.graphname = %s and a.userid = %s",[objectname,grantinguser])
		output = cur.fetchall()
		if output:
			usercangrant,userread,userwrite,userexecute = output[0]
		
		cur.execute("select cangrant,read,write,exe from grouppermission a, graphstore b, usergroup c where a.graphid = b.graphid and c.groupid = a.groupid and  b.graphname = %s and c.userid = %s",[objectname,grantinguser])
		output = cur.fetchall()
		if output:
			groupcangrant,groupread,groupwrite,groupexecute = output[0]
	except Exception as e:
		cur.close()
		connection.close()	
		raise NameError("Check grant permission failed for object "+objectname+" for user "+grantinguser+" due to "+str(e).replace(':','-'))	
	
	if usercangrant == 'Y' or groupcangrant == 'Y':
		return True
		
def update_user_permission(user,grantinguser,objectname,permission=['N','N','N','N']): #permission = ['read','write','execute','cangrant']
	if not checkobjectpresence(objectname):
		raise NameError(" Invalid object "+objectname)
	isgrant = checkusergrant(grantinguser,objectname)
	if not isgrant:
		raise NameError(grantinguser+ " User dont have Granting permission for object "+objectname)
	connection = connect(user = dbuser,password = dbpassword, host = dbhost,port = dbport,database = db)
	cur = connection.cursor()
	try:
		cur.execute("select count(1) from userpermission a join graphstore b on a.graphid = b.graphid where b.graphname = %s and a.userid = %s",[objectname,user])
		isexist = cur.fetchall()[0][0]
		if isexist >0:
			cur.execute("update userpermission set read = %s, write = %s, exe = %s,cangrant = %s where userid = %s and graphid = (select graphid from graphstore where graphname = %s )", permission+[user,objectname])
		else:
			cur.execute("Insert into userpermission(read,write,exe,cangrant,userid,graphid) select %s,%s,%s,%s,%s,graphid from graphstore where  graphname=%s", permission+[user,objectname])
	except Exception as e:
		cur.close()
		connection.close()	
		raise NameError("Update permission failed for object "+objectname+" for user "+user+" due to "+str(e).replace(':','-'))
	cur.execute("commit")
	cur.close()
	connection.close()

def update_group_permission(group,grantinguser,objectname,permission=['N','N','N','N']):
	if not checkobjectpresence(objectname):
		raise NameError(" Invalid object "+objectname)
	isgrant = checkusergrant(grantinguser,objectname)
	if not isgrant:
		raise NameError(grantinguser+ " User dont have Granting permission for object "+objectname)
	connection = connect(user = dbuser,password = dbpassword, host = dbhost,port = dbport,database = db)
	cur = connection.cursor()
	try:
		cur.execute("select count(1) from grouppermission a join graphstore b on a.graphid = b.graphid where b.graphname = %s and a.groupid = %s",[objectname,group])
		isexist = cur.fetchall()[0][0]
		if isexist >0:
			cur.execute("update grouppermission set read = %s, write = %s, exe = %s,cangrant = %s where groupid = %s and graphid = (select graphid from graphstore where graphname = %s )", permission+[group,objectname])
		else:
			cur.execute("Insert into userpermission(read,write,exe,cangrant,groupid,graphid) select %s,%s,%s,%s,%s,graphid from graphstore where  graphname=%s", permission+[group,objectname])
	except Exception as e:
		cur.close()
		connection.close()	
		raise NameError("Update permission failed for object "+objectname+" for group "+group+" due to "+str(e).replace(':','-'))
	cur.execute("commit")
	cur.close()
	connection.close()	
	
def update_public_permission(objectname,grantinguser,permission=['N','N','N']):
	if not checkobjectpresence(objectname):
		raise NameError(" Invalid object "+objectname)
	isgrant = checkusergrant(grantinguser,objectname)
	if not isgrant:
		raise NameError(grantinguser+ " User dont have Granting permission for object "+objectname)
	connection = connect(user = dbuser,password = dbpassword, host = dbhost,port = dbport,database = db)
	cur = connection.cursor()
	try:
		cur.execute("select count(1) from publicpermission a join graphstore b on a.graphid = b.graphid where b.graphname = %s",[objectname])
		isexist = cur.fetchall()[0][0]
		if isexist >0:
			cur.execute("update publicpermission set read = %s, write = %s, exe = %s where graphid = (select graphid from graphstore where graphname = %s )", permission+[objectname])
		else:
			cur.execute("Insert into publicpermission(read,write,exe,graphid) select %s,%s,%s,graphid from graphstore where  graphname=%s", permission+[objectname])
	except Exception as e:
		cur.close()
		connection.close()	
		raise NameError("Update permission failed for object "+objectname+" for user Public due to "+str(e).replace(':','-'))
	cur.execute("commit")
	cur.close()
	connection.close()
		
def checkpermission(user,objectname,action):
	if not checkobjectpresence(objectname):
		raise NameError(" Invalid object "+objectname)

	connection = connect(user = dbuser,password = dbpassword, host = dbhost,port = dbport,database = db)
	cur = connection.cursor()
	########## fetch permission
	########## check admin privileges
	try:
		cur.execute("select count(1) from adminusers where userid = %s",[user])
		isexistadmin = cur.fetchall()[0][0]
	except Exception as e:
		cur.close()
		connection.close()	
		raise NameError("Fetch permission failed for object "+objectname+" for user "+user+" due to "+str(e).replace(':','-'))
	if isexistadmin > 0:
		return True
	
	try:
		userread ='N';userwrite='N';userexecute='N';
		cur.execute("select read,write,exe from userpermission a join graphstore b on a.graphid = b.graphid and b.graphname = %s and a.userid = %s",[objectname,user])
		output = cur.fetchall()
		if output:
			userread,userwrite,userexecute = output[0]
		
		groupread='N';groupwrite='N';groupexecute='N';
		cur.execute("select read,write,exe from grouppermission a, graphstore b, usergroup c where a.graphid = b.graphid and c.groupid = a.groupid and  b.graphname = %s and c.userid = %s",[objectname,user])
		output = cur.fetchall()
		if output:
			groupread,groupwrite,groupexecute = output[0]
		
		publicread='N';publicwrite='N';publicexecute='N';
		cur.execute("select read,write,exe from publicpermission a, graphstore b where a.graphid = b.graphid and b.graphname = %s",[objectname])
		output = cur.fetchall()
		if output:
			publicread,publicwrite,publicexecute = output[0]
		
	except Exception as e:
		cur.close()
		connection.close()	
		raise NameError("Fetch permission failed for object "+objectname+" for user "+user+" due to "+str(e).replace(':','-'))
	
	cur.close()
	connection.close()	
	
	if action == 'read' and (userread == 'Y' or groupread == 'Y' or publicread =='Y'):
		return True
	elif action == 'write' and (userwrite == 'Y' or groupwrite == 'Y' or publicwrite == 'Y'):
		return True
	elif action == 'execute' and (userexecute == 'Y' or groupexecute == 'Y' or publicexecute=='Y'):
		return True
	else:
		return False

def getallsecuredobjects(objecttype,sessuser):
	connection = connect(user = dbuser,password = dbpassword, host = dbhost,port = dbport,database = db)
	cur = connection.cursor()
	if objecttype == 'reusablefun':
		cur.execute("select distinct a.functionname, b.inputargs from reusablefun a, graphstore b, (select graphid from userpermission where read ='Y' and userid = %s union select graphid from publicpermission where read ='Y' union select graphid from grouppermission a, usergroup b where a.read ='Y' and a.groupid = b.groupid and b.userid =%s) c where a.graphname = b.graphname and isapi='N' and b.graphid = c.graphid",[sessuser,sessuser])
	elif objecttype == 'apifun':
		cur.execute("select distinct a.functionname, b.inputargs from reusablefun a, graphstore b, (select graphid from userpermission where read ='Y' and userid = %s union select graphid from publicpermission where read ='Y' union select graphid from grouppermission a, usergroup b where a.read ='Y' and a.groupid = b.groupid and b.userid =%s) c where a.graphname = b.graphname and a.isapi='Y' and a.isdataapi = 'N' and a.isiotdevice = 'N' and b.graphid = c.graphid",[sessuser,sessuser])
	elif objecttype == 'datafun':
		cur.execute("select distinct a.functionname, b.inputargs from reusablefun a, graphstore b, (select graphid from userpermission where read ='Y' and userid = %s union select graphid from publicpermission where read ='Y' union select graphid from grouppermission a, usergroup b where a.read ='Y' and a.groupid = b.groupid and b.userid =%s) c where a.graphname = b.graphname and a.isapi='Y' and a.isdataapi = 'Y' and b.graphid = c.graphid",[sessuser,sessuser])
	elif objecttype == 'graph':	
		cur.execute("select distinct b.graphname, b.inputargs from graphstore b, (select graphid from userpermission where read ='Y' and userid = %s union select graphid from publicpermission where read ='Y' union select graphid from grouppermission a, usergroup b where a.read ='Y' and a.groupid = b.groupid and b.userid =%s) c where b.graphname not in (select graphname from reusablefun where isapi='Y') and b.graphid = c.graphid",[sessuser,sessuser])
	elif objecttype == 'iotfun':	
		cur.execute("select distinct a.functionname, b.inputargs from reusablefun a, graphstore b, (select graphid from userpermission where read ='Y' and userid = %s union select graphid from publicpermission where read ='Y' union select graphid from grouppermission a, usergroup b where a.read ='Y' and a.groupid = b.groupid and b.userid =%s) c where a.graphname = b.graphname and a.isapi='Y' and a.isiotdevice = 'Y' and b.graphid = c.graphid",[sessuser,sessuser])
	return dict(cur.fetchall())
			
def create_user(user):
	connection = connect(user = dbuser,password = dbpassword, host = dbhost,port = dbport,database = db)
	cur = connection.cursor()
	########## fetch permission
	########## check admin privileges
	try:
		cur.execute("select count(1) from users where userid = %s",[user])
		isexistuser = cur.fetchall()[0][0]
		if isexistuser>0:
			raise NameError("user "+user+" already exists")
		else:
			cur.execute("Insert into users values(%s)",[user])
	except Exception as e:
		cur.close()
		connection.close()	
		raise NameError("Create user failed for "+user+" due to "+str(e).replace(':','-'))
	cur.close()
	connection.close()	
	
def create_group(group):
	connection = connect(user = dbuser,password = dbpassword, host = dbhost,port = dbport,database = db)
	cur = connection.cursor()
	########## fetch permission
	########## check admin privileges
	try:
		cur.execute("select count(1) from groups where groupid = %s",[group])
		isexistgroup = cur.fetchall()[0][0]
		if isexistgroup>0:
			raise NameError("user "+group+" already exists")
		else:
			cur.execute("Insert into groups values(%s)",[group])
	except Exception as e:
		cur.close()
		connection.close()	
		raise NameError("Create group failed for "+group+" due to "+str(e).replace(':','-'))
	cur.close()
	connection.close()		
	
def delete_all_permissions(objectname):
	connection = connect(user = dbuser,password = dbpassword, host = dbhost,port = dbport,database = db)
	cur = connection.cursor()
	try:
		cur.execute("delete from userpermission where graphid in (select graphid from graphstore where graphname = %s )",[objectname])
		cur.execute("delete from grouppermission where graphid in (select graphid from graphstore where graphname = %s )",[objectname])
		cur.execute("delete from publicpermission where graphid in (select graphid from graphstore where graphname = %s )",[objectname])
	except Exception as e:
		cur.close()
		connection.close()	
		raise NameError("Delete permission failed for "+objectname+str(e).replace(':','-'))
	cur.execute("commit")
	cur.close()
	connection.close()