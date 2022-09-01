import base64
import ast
import sys
import random
import string

datasizethreshold = 2

def checkdatasize(data,storageclient,workingbucket,workingdir,runid):
	if sys.getsizeof(data) > datasizethreshold*(1024**2):
		workingbucket_handle = storageclient.get_bucket(workingbucket)
		filename = runid+''.join(random.choices(string.ascii_uppercase + string.digits, k = 8))
		blob = workingbucket_handle.blob(workingdir+'/'+filename)
		data = blob.upload_from_string(data)
		newdata = 'gs://'+workingbucket+'/'+workingdir+'/'+filename
	else:
		newdata = data
	return newdata
	
def parselisttype(data,storageclient,workingbucket,workingdir,runid):
	newdata = []
	if isinstance(data, list) and not isinstance(data, str):
		for item in data:
			newitem= parselisttype(item,storageclient,workingbucket,workingdir,runid) 
			newdata.append(newitem)
	else:
		newdata = checkdatasize(data,storageclient,workingbucket,workingdir,runid)
		
	return (newdata)

def CheckInputStream(Inp,headers,storageclient,workingbucket,workingdir,runid):
	
	if 'Content-Type' in headers:
		if headers['Content-Type'] == 'application/octet-stream':
			if type(Inp) == bytes:
				output =  Inp
			else:
				output = str(Inp).encode('utf-8')
		elif headers['Content-Type'] == 'application/json':
			#print("json")
			try:
				Inp = ast.literal_eval(Inp)
			except:
				pass
			#print("Input",Inp)
			output = Inp
		else:
			output = parselisttype(Inp,storageclient,workingbucket,workingdir,runid)
			output = str(output)
	else:  #### content type plain text encoded in 'utf-8' by default
		#print ("Inp", Inp)
		Inp = parselisttype(Inp,storageclient,workingbucket,workingdir,runid)
		if type(Inp) != bytes:
			try:
				output = str(Inp).encode('utf-8')
			except:
				output = Inp
		else:
			output = Inp

	return output
			#if type(Inp) == list:
			#for i in range(len(Inp)):
			#	if type(Inp[i]) == bytes:
			#		Inp[i] = base64.b64encode(Inp[i])
		#	return (str(Inp))
		#elif type(Inp) == bytes:
		#	return (Inp)
	#	Inp = base64.b64encode(Inp)
		
	#return str(Inp)
		


def CheckOutputStream(Op):
	
	if type(Op) == bytes:
		try:
			Op = Op.decode('utf-8')
		except:
			pass
	try:
		op = ast.literal_eval(Op)
	except:
		op =Op
	if type(op) == list:
		for i in range(len(op)):
			if type(op[i]) == bytes:
				#base64.b64decode(op[i])
				try:
					op[i] = op[i].decode('utf-8')
					op[i] = ast.literal_eval(op[i])
				except:
					pass
	#elif type(op) == bytes:
	#	op = op.decode('utf-8')#base64.b64decode(op)
		
	return op



if __name__ == "__main__":
	print("The functions is only invokable not executable")