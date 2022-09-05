import requests
import ast
import pickle
import time
###### mandatory Methods
## reset : None --> None ######### should reset the environment
## get_observation : None --> Any return type ##### get the current observation 
## take_action : Any Input type --> None ######### take action based on input
## get_reward : None --> Number ######### return  normalized total reward between -1 and 1
## check_goalstate : None --> Boolean ########## check if goal is reached
## get_state : None --> dict ###### output current state


class microapi:
	def __init__(self,init_state=[]):
		self.state = dict()
		self.state['state'] = pickle.loads(pickle.dumps(init_state,-1))
		self.init_state = init_state
		self.pending_state = 0
	
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
	
	def take_action(self,action,remoteserviceheader={}):
		current_state = self.state['state']
		#raise NameError("Argh! The API call failed")
		#print("at take action time",current_state, time.time())
		########### Take action
		if not current_state:
			apiname = action ###self.state['apimap'][action]
			self.state['state'].append(apiname)
		#elif self.state['state'][0] == 'customapiname':
			# <your custom code to be executed>
		else:
			###################################### call remote api ####################3
			url = self.state['state'][0]['url']
			headers = self.state['state'][0]['headers']
			headers.update(remoteserviceheader)
			data = CheckInputStream(action,headers)
			if 'Content-Type' in headers:
				if headers['Content-Type'] == 'application/json':
					x = requests.post(url, json = data,headers=headers)
				else:
					x = requests.post(url, data = data,headers=headers)
			else:
				x = requests.post(url, data = data,headers=headers)
			###############################
			
			if x.status_code != 200:
				print(x.content.decode('utf-8'))
				raise NameError("Argh! The API call for "+url+' failed due to '+x.content.decode('utf-8'))
			self.state['state'].append(CheckOutputStream(x.content))
		return 

	def get_reward(self):
		return self.total_reward
		
	def get_state(self):
		return self.state
		
	def set_state(self,state):
		self.state = state
		
	def check_goalstate(self,data,remoteserviceheader={}):
		return False


######################################## Supporting functions ###########################################################

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
	return op


def parselisttype(data,storageclient,workingbucket,workingdir,runid):
	newdata = []
	if isinstance(data, list) and not isinstance(data, str):
		for item in data:
			newitem= parselisttype(item,storageclient,workingbucket,workingdir,runid) 
			newdata.append(newitem)
	else:
		newdata = data
		
	return (newdata)

def CheckInputStream(Inp,headers):
	
	if 'Content-Type' in headers:
		if headers['Content-Type'] == 'application/octet-stream':
			if type(Inp) == bytes:
				output =  Inp
			else:
				output = str(Inp).encode('utf-8')
		elif headers['Content-Type'] == 'application/json':
			try:
				Inp = ast.literal_eval(Inp)
			except:
				pass
			output = Inp
		else:
			output = parselisttype(Inp)
			output = str(output)
	else:  #### content type plain text encoded in 'utf-8' by default
		Inp = parselisttype(Inp)
		if type(Inp) != bytes:
			try:
				output = str(Inp).encode('utf-8')
			except:
				output = Inp
		else:
			output = Inp
	return output

api_world = microapi()