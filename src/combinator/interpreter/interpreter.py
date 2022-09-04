# cython: profile=True
# cython: linetrace=True
# distutils: define_macros=CYTHON_TRACE_NOGIL=1
from combinator.interpreter.makegraph import *

class time_exception(Exception):
	pass


class combinatorruntimeerror(Exception):
	def __init__(self, message=[]):            
        # Call the base class constructor with the parameters it needs
		super().__init__(message)
		self.error = message


class time_object:
	def __init__(self,time_limit):
		self.time = time_limit
		self.remoteserviceheader = None
	def consume_time(self,_steps):
		self.time -= _steps
		corpusInstance.total_runtime +=1
	def get_time(self):
		return self.time
    

#cdef dict no_of_args = {'iW':0,'+':2,'id':1, 'K': 1,'-':2,'*':2,'/':2,'^':2,'if':3,'=':2,'>':2,'&':2,'|':2,'!':1,'hd':1,'tl':1,'cn':2,'nl':1,'ap':2,'fm':2,'zp':3,'ag':2,'rc':3,'sn':1,'ac':1,'gc':1,'wm':2,'lg':1,'gp':1}

def returngraph(parnode_label, graph):
	if isinstance(parnode_label, tuple):
		return(parnode_label[0],graph['par'])
	else:
		return(parnode_label,graph)
		
		
def _interpret_single_input_funct(nodename,terminalnode_label,graph,tottime): #['K','id','!','hd','tl','sn','ac','gc','nl']: ########### constant, identity, negate
	try:
		parents=getval_graph(graph,terminalnode_label,'E')
	except Exception as e:
		raise combinatorruntimeerror([{'message':"Unable to get parent node of this lambdagraph node! Please check for input port connection.",'error':repr(e),'nodeid':terminalnode_label}])
	parnode_label,pargraph = returngraph(parents[0],graph)
	parentoutput,w,wv,tottime=interpreter(parnode_label,pargraph,tottime)   
	if nodename == 'K':
		try:
			data = graph['nodes'][terminalnode_label]['K']
		except Exception as e:
			raise combinatorruntimeerror([{'message':"Error in fetching assigned constant value! Please check if the constant value is properly set for this constant node!",'error':repr(e),'nodeid':terminalnode_label}])
		nodenamefull = "constant"
	elif nodename == 'id':
		data = parentoutput
		nodenamefull = "identity"
	elif nodename == 'pt':
		print("data",parentoutput)
		data = parentoutput
		nodenamefull = "print"
	elif nodename == '!':
		try:
			data = not parentoutput
		except Exception as e:
			raise combinatorruntimeerror([{'message':"Parent output of this negate node is not a boolean value!",'error':repr(e),'nodeid':terminalnode_label}])
		nodenamefull = "negate"
	elif nodename == 'nl':
		if parentoutput == 'keyvalue':
			data = {}
		else:
			data = []
		nodenamefull = "emptylistordict"
	elif nodename == 'hd':
		try:
			data = parentoutput[0]
		except Exception as e:
			raise combinatorruntimeerror([{'message':"Unable get the first element of the list! Either the input data of the head node is not of list type or it is empty.",'error':repr(e),'nodeid':terminalnode_label}])
		nodenamefull = "head"
	elif nodename == 'tl':
		templist=parentoutput
		try:
			data = templist[1:len(templist)]
		except Exception as e:
			raise combinatorruntimeerror([{'message':"Unable get the tail of the list! The input data of this tail node may not be of list type.",'error':repr(e),'nodeid':terminalnode_label}])
		nodenamefull = "tail"
	elif nodename == 'sn':
		data = w.get_data(tottime.remoteserviceheader)
		prev_version = wv
		w.upgrade()
		#if w.version != prev_version + 1:
		#	raise Exception("Invalid sequence of sensor")
		wv = w.version
		nodenamefull = "sensor"
	elif nodename == 'ac':
		data = 1
		w.put_action(parentoutput,tottime.remoteserviceheader)
		prev_version = wv
		w.upgrade()
		#if w.version != prev_version + 1:
		#	raise Exception("Invalid sequence of actuator")
		wv = w.version
		nodenamefull = "actuator"
	elif nodename == 'gc':
		data = w.check_goal_state(parentoutput,tottime.remoteserviceheader)
		prev_version = wv
		w.upgrade()
		#if w.version != prev_version + 1:
		#	raise Exception("Invalid sequence of goalchecker")
		wv = w.version
		nodenamefull = "goalchecker"
	try:
		setval_graph('dat',data,graph,terminalnode_label,'N')
	except Exception as e:
		raise combinatorruntimeerror([{'message':"Unable to set node output value for this "+nodenamefull+" node!",'error':repr(e),'nodeid':terminalnode_label}])
	setval_graph('wv',wv,graph,terminalnode_label,'N')
	setval_graph('w',w,graph,terminalnode_label,'N')
	return tottime
	
def _interpret_lg(nodename,terminalnode_label,graph,tottime): ##### lambdagraph
	try:
		parents=getval_graph(graph,terminalnode_label,'E')
	except Exception as e:
		raise combinatorruntimeerror([{'message':"Unable to get parent node of this lambdagraph node! Please check for input port connection.",'error':repr(e),'nodeid':terminalnode_label}])
	id1 = createnode(graph,'id')
	#graph['nodes'][id1]['ii'] = 1
	setval_graph('ii',1,graph,id1,'N')
	try:	
		data,world,world_version = returnSubgraph(graph,parents[0],id1)
		resetGraph(data)
	except Exception as e:
		raise combinatorruntimeerror([{'message':"Unable to generate parent subgraph of this lambdagraph node as it might be directly connected to initWorld.",'error':repr(e),'nodeid':terminalnode_label}])
	setval_graph('dat',data,graph,terminalnode_label,'N')
	del graph['nodes'][id1]
	setval_graph('wv',world_version,graph,terminalnode_label,'N')
	setval_graph('w',world,graph,terminalnode_label,'N')
	return tottime
	
def _interpret_two_port_funct(nodename,terminalnode_label,graph,tottime): #['+','-','*','/','^','&','|','>','=','cn','wm']
	try:
		parents=getval_graph(graph,terminalnode_label,'E')
	except Exception as e:
		raise combinatorruntimeerror([{'message':"Unable to get parent node of this node! Please check for input port connection.",'error':repr(e),'nodeid':terminalnode_label}])
	if len(parents) < 2:
		raise combinatorruntimeerror([{'message':"Unable to get all parent nodes of this node! Please check for all input port connections.",'error':'unconnected input ports','nodeid':terminalnode_label}])
	parnode_label,pargraph = returngraph(parents[0],graph)
	parentoutput1,w1,wv1,tottime = interpreter(parnode_label,pargraph,tottime)
	parnode_label,pargraph = returngraph(parents[1],graph)
	parentoutput2,w2,wv2,tottime = interpreter(parnode_label,pargraph,tottime) 

	try:
		if nodename == '+':
			nodenamefull = "addition"
			if isinstance(parentoutput1,dict) and isinstance(parentoutput2,dict):
				parentoutput1.update(parentoutput2)
				data = parentoutput1
			else:
				data = parentoutput1 + parentoutput2
		elif nodename == '-':
			nodenamefull = "subtraction"
			data = parentoutput1-parentoutput2
		elif nodename == '*':
			nodenamefull = "multiplication"
			data = parentoutput1 * parentoutput2
		elif nodename == '/':
			nodenamefull = "division"
			data = parentoutput1 / parentoutput2
		elif nodename == '^':
			nodenamefull = "exponent"
			data = parentoutput1 ** parentoutput2	
		elif nodename == '&':
			nodenamefull = "AND"
			data = parentoutput1 and parentoutput2
		elif nodename == '|':
			nodenamefull = "OR"
			data = parentoutput1 or parentoutput2
		elif nodename == '>':
			nodenamefull = "greaterthan"
			data = parentoutput1 > parentoutput2
	except Exception as e:
			raise combinatorruntimeerror([{'message':"Unable to do "+nodenamefull+" of two parent outputs! "+repr(e).replace("\\",''),'error':repr(e),'nodeid':terminalnode_label}])
	
	if nodename == 'wm':
		nodenamefull = "worldmerger"
		data = parentoutput1
	elif nodename == 'cn':
		nodenamefull = "append"
		try:
			parentoutput2.append(parentoutput1)
		except Exception as e:
			raise combinatorruntimeerror([{'message':"Unable to append parentoutput1 to parentoutput2! The parentoutput2 may not be in list format.",'error':repr(e),'nodeid':terminalnode_label}])
		data = parentoutput2
		#print(parentoutput2)
	elif nodename == 'pop':
		nodenamefull = "pop"
		if isinstance(parentoutput2,list):
			try:
				data = parentoutput2[int(parentoutput1)]
			except Exception as e:
				raise combinatorruntimeerror([{'message':"Unable to pop from parentoutput2! The parentoutput1 is not in integer format or invalid index supplied in parentoutput1.",'error':repr(e),'nodeid':terminalnode_label}])
		elif isinstance(parentoutput2,dict):
			try:
				data = parentoutput2[parentoutput1]
			except Exception as e:
				raise combinatorruntimeerror([{'message':"Unable to pop from parentoutput2! The parentoutput1 is not a valid key for parentoutput2.",'error':repr(e),'nodeid':terminalnode_label}])
		else:
			raise combinatorruntimeerror([{'message':"Parentoutput2 should either be a list or key-value pairs!",'error':repr(e),'nodeid':terminalnode_label}])
	elif nodename == '=':
		nodenamefull = "equality"
		try:
			data = parentoutput1 == parentoutput2
		except Exception as e:
			raise combinatorruntimeerror([{'message':"Unable to check equality between parentoutput1 and parentoutput2! "+repr(e),'error':repr(e),'nodeid':terminalnode_label}])
	try:
		setval_graph('dat',data,graph,terminalnode_label,'N')
	except Exception as e:
		raise combinatorruntimeerror("Unable to set node output value for this "+nodenamefull+" node!",[repr(e)],[terminalnode_label])
	setval_graph('wv',max(wv1,wv2),graph,terminalnode_label,'N')
	setval_graph('w',w1,graph,terminalnode_label,'N')
	return tottime

def _interpret_ak(nodename,terminalnode_label,graph,tottime):
	try:
		parents = getval_graph(graph,terminalnode_label,'E')
	except Exception as e:
		raise combinatorruntimeerror([{'message':"Unable to get parent node of this addkey node! Please check for input port connection.",'error':repr(e),'nodeid':terminalnode_label}])
	if len(parents) < 3:
		raise combinatorruntimeerror([{'message':"Unable to get all parent nodes of this node! Please check for all input port connections.",'error':'unconnected input ports','nodeid':terminalnode_label}])
	parnode_label,pargraph = returngraph(parents[0],graph)
	parentoutput1,w1,wv1,tottime = interpreter(parnode_label,pargraph,tottime)
	parnode_label,pargraph = returngraph(parents[1],graph)
	parentoutput2,w2,wv2,tottime = interpreter(parnode_label,pargraph,tottime) 
	parnode_label,pargraph = returngraph(parents[2],graph)
	parentoutput3,w3,wv3,tottime = interpreter(parnode_label,pargraph,tottime) 
	try:
		parentoutput1[parentoutput2] = parentoutput3
		data = parentoutput1
	except Exception as e:
			raise combinatorruntimeerror([{'message':"Unable to add key parentoutput2 in parentoutput1! The parentoutput1 may not be in key-value format or parentoutput2 may not be in string or number format",'error':repr(e),'nodeid':terminalnode_label}])
	try:
		setval_graph('dat',data,graph,terminalnode_label,'N')
	except Exception as e:
		raise combinatorruntimeerror("Unable to set node output value for this addkey node!",[repr(e)],[terminalnode_label])
	setval_graph('wv',max(wv1,wv2,wv3),graph,terminalnode_label,'N')
	setval_graph('w',w1,graph,terminalnode_label,'N')
	return tottime

def _interpret_gp(nodename,terminalnode_label,graph,tottime):  #### graph program
	try:
		parents = getval_graph(graph,terminalnode_label,'E')
	except Exception as e:
		raise combinatorruntimeerror([{'message':"Unable to get parent node of this gp node! Please check for input port connection.",'error':repr(e),'nodeid':terminalnode_label}])
	subgraph = getval_graph(graph,terminalnode_label,'N','fun')
	try:
		if len(getval_graph(graph,terminalnode_label,'E')) >= getargs(terminalnode_label,graph): ############ all linkconnections satisfied
			parentoutput1,w,wv,tottime = interpreter(list(subgraph['terminalnodes'].keys())[0],subgraph,tottime)
			setval_graph('dat',parentoutput1,graph,terminalnode_label,'N')
		else:
			parnode_label,pargraph = returngraph(parents[0],graph)
			parentoutput1,w,wv,tottime = interpreter(parnode_label,pargraph,tottime)
			setval_graph('dat',subgraph,graph,terminalnode_label,'N')
	except combinatorruntimeerror as e:
		e.error.append({'message':"Error in evaluating subgraph in gp node!",'error':'parenterror','nodeid':terminalnode_label})
		raise combinatorruntimeerror(e.error)
	except Exception as e:
		raise combinatorruntimeerror([{'message':"Error in evaluating subgraph in gp node!",'error':repr(e),'nodeid':terminalnode_label}])
	setval_graph('wv',wv,graph,terminalnode_label,'N')
	setval_graph('w',w,graph,terminalnode_label,'N')
	return tottime

def _interpret_ap(nodename,terminalnode_label,graph,tottime):  #### apply
	try:
		parents = getval_graph(graph,terminalnode_label,'E')
	except Exception as e:
		raise combinatorruntimeerror([{'message':"Unable to get parent node of this apply node! Please check for input port connection.",'error':repr(e),'nodeid':terminalnode_label}])
	if len(parents) < 2:
		raise combinatorruntimeerror([{'message':"Unable to get all parent nodes of this apply node! Please check for all input port connections.",'error':'unconnected input ports','nodeid':terminalnode_label}])
	parnode_label,pargraph = returngraph(parents[0],graph)
	#try:
	parentoutput1,w,wv,tottime = interpreter(parnode_label,pargraph,tottime)
	if isinstance(parentoutput1,tuple):
		_nlabel = parentoutput1[0]
		#print(_nlabel)
		try:
			addlink(graph,_nlabel,parents[1])
		except Exception as e:
			raise combinatorruntimeerror([{'message':"Error in adding link to subgraph in apply node! Please check if all the input ports of the apply node are connected.",'error':repr(e),'nodeid':terminalnode_label}])
		del graph['terminalnodes'][_nlabel]
		if len(getval_graph(graph,_nlabel,'E')) >= getargs(_nlabel,graph): ############ all linkconnections satisfied
			try:
				currentoutput,w,wv,tottime = interpreter(_nlabel,graph,tottime)
			except combinatorruntimeerror as e:
				e.error.append({'message':"Error in evaluating subgraph in apply node! The parentnode1 should return a valid graph type that can be applied on the output of parentnode2.",'error':'parenterror','nodeid':terminalnode_label})
				raise combinatorruntimeerror(e.error)
			except Exception as e:
				raise combinatorruntimeerror([{'message':"Error in evaluating subgraph in apply node!",'error':repr(e),'nodeid':terminalnode_label}])
		else:
			currentoutput = parentoutput1
	else:
		try:
			_nlabel=createnode(graph,'gp',parentoutput1)
		except Exception as e:
			raise combinatorruntimeerror([{'message':"Error in creating subgraph in apply node! The parentnode1 should return a graph type.",'error':repr(e),'nodeid':terminalnode_label}])
		try:
			addlink(graph,_nlabel,parents[1])
		except Exception as e:
			raise combinatorruntimeerror([{'message':"Error in adding link to subgraph in apply node! Please check if all the input ports of the apply node are connected.",'error':repr(e),'nodeid':terminalnode_label}])
		del graph['terminalnodes'][_nlabel]
		try:
			currentoutput,w,wv,tottime = interpreter(_nlabel,graph,tottime)
		except combinatorruntimeerror as e:
			e.error.append({'message':"Error in evaluating subgraph in apply node! The parentnode1 should return a valid graph type that can be applied on the output of parentnode2.",'error':'parenterror','nodeid':terminalnode_label})
			raise combinatorruntimeerror(e.error)
		except Exception as e:
			raise combinatorruntimeerror([{'message':"Error in evaluating subgraph in apply node!",'error':repr(e),'nodeid':terminalnode_label}])
		remove_node(graph,_nlabel)
	setval_graph('dat',currentoutput,graph,terminalnode_label,'N')
	setval_graph('w',w,graph,terminalnode_label,'N')
	setval_graph('wv',wv,graph,terminalnode_label,'N')
	return tottime

def _interpret_if(nodename,terminalnode_label,graph,tottime): ###### conditional
	try:
		parents = getval_graph(graph,terminalnode_label,'E')
	except Exception as e:
		raise combinatorruntimeerror([{'message':"Unable to get parent node of this condition node! Please check for input port connections.",'error':repr(e),'nodeid':terminalnode_label}])
	if len(parents) < 3:
		raise combinatorruntimeerror([{'message':"Unable to get all parent nodes of this condition node! Please check for all input port connections.",'error':'unconnected input ports','nodeid':terminalnode_label}])
	parnode_label,pargraph = returngraph(parents[0],graph)
	parentoutput1,w,wv1,tottime = interpreter(parnode_label,pargraph,tottime)
	if parentoutput1:
		parnode_label,pargraph = returngraph(parents[1],graph)
		parentoutput2,w,wv2,tottime = interpreter(parnode_label,pargraph,tottime)
	else:
		parnode_label,pargraph = returngraph(parents[2],graph)
		parentoutput2,w,wv2,tottime = interpreter(parnode_label,pargraph,tottime)
	setval_graph('dat',parentoutput2,graph,terminalnode_label,'N')
	setval_graph('wv',max(wv1,wv2),graph,terminalnode_label,'N')
	setval_graph('w',w,graph,terminalnode_label,'N')
	return tottime


def _interpret_fmap(nodename,terminalnode_label,graph,tottime):
	try:
		parents = getval_graph(graph,terminalnode_label,'E')
	except Exception as e:
		raise combinatorruntimeerror([{'message':"Unable to get parent node of this fmap node! Please check for all input port connections.",'error':repr(e),'nodeid':terminalnode_label}])
	if len(parents) < 2:
		raise combinatorruntimeerror([{'message':"Unable to get all parent nodes of this fmap node! Please check for all input port connections.",'error':'unconnected input ports','nodeid':terminalnode_label}])
	parnode_label1,pargraph1 = returngraph(parents[0],graph)
	parnode_label2,pargraph2 = returngraph(parents[1],graph)
	_nlabel1=createnode(graph,'lg')
	setval_graph('uex',0,graph,_nlabel1,'N')
	addlink(graph,_nlabel1,parnode_label1)
	del graph['terminalnodes'][_nlabel1]
	try:	
		in_function,w,wv,tottime=interpreter(_nlabel1,pargraph1, tottime)
	except combinatorruntimeerror as e:
		e.error.append({'message':"Error in fetching subgraph of parentnode1 of the fmap node!",'error':'parenterror','nodeid':terminalnode_label})
		raise combinatorruntimeerror(e.error)
	except Exception as e:
		raise combinatorruntimeerror([{'message':"Error in fetching subgraph of parentnode1 of the fmap node!",'error':repr(e),'nodeid':terminalnode_label}])
	initialvaluelist,w,wv,tottime=interpreter(parnode_label2,pargraph2, tottime)
	#print('parnode_label2:', parents[1])
	initialnode = parents[1]
	#print(in_function)
	currentvaluelist = []
	try:
		iter(initialvaluelist)
	except Exception as e:
		raise combinatorruntimeerror([{'message':"Unable to iterate on the ouptut of parentnode2! The output of parentnode2 should be of list or string type.",'error':repr(e),'nodeid':terminalnode_label}])
	for i in initialvaluelist:
		new_in_function = pickle.loads(pickle.dumps(in_function,-1))
		newvaluenode = createnode(graph,'K',i)
		setval_graph('uex',0,graph,newvaluenode,'N')
		addlink(graph,newvaluenode,initialnode)
		del graph['terminalnodes'][newvaluenode]
		_nlabel0=createnode(graph,'gp',new_in_function)
		setval_graph('uex',0,graph,_nlabel0,'N')
		addlink(graph,_nlabel0,newvaluenode)
		del graph['terminalnodes'][_nlabel0]
		######## point parent graphs of all gp nodes within  in_function to in_function, which are by default pointing to graph
		for nodelabel,node in new_in_function['nodes'].items():
			#print('nodelabel',nodelabel)           
			if node['nm'] == 'gp':
				node['fun']['par'] = new_in_function  
		try:
			currentdata,w,wv,tottime = interpreter(_nlabel0,graph,tottime)
		except combinatorruntimeerror as e:
			e.error.append({'message':"Error in evaluating subgraph of parentnode1 in the fmap node on the value "+str(i)+"! The subgraph corresponding to the parentnode1 should be a valid function that can be applied on each element of the list output of parentnode2.",'error':'parenterror','nodeid':terminalnode_label})
			raise combinatorruntimeerror(e.error)
		except Exception as e:
			raise combinatorruntimeerror([{'message':"Error in evaluating subgraph of parentnode1 in the fmap node on the value "+str(i)+"!",'error':repr(e),'nodeid':terminalnode_label}])
		currentvaluelist.append(currentdata)
		#initialnode = _nlabel0
		remove_node(graph,_nlabel0)
		remove_node(graph,newvaluenode)
		#if prev_node != None:
			#print('prev_node',prev_node)
		#	remove_node(graph,prev_node)
		#prev_node = _nlabel0
	#remove_node(graph,prev_node)
	remove_node(graph,_nlabel1)
	setval_graph('dat',currentvaluelist,graph,terminalnode_label,'N')
	setval_graph('wv',wv,graph,terminalnode_label,'N')
	setval_graph('w',w,graph,terminalnode_label,'N')
	return tottime


def _interpret_zip(nodename,terminalnode_label,graph,tottime):
	try:
		parents = getval_graph(graph,terminalnode_label,'E')
	except Exception as e:
		raise combinatorruntimeerror([{'message':"Unable to get parent node of this zip node! Please check for input port connections.",'error':repr(e),'nodeid':terminalnode_label}])
	if len(parents) < 2:
		raise combinatorruntimeerror([{'message':"Unable to get all parent nodes of this zip node! Please check for all input port connections.",'error':'unconnected input ports','nodeid':terminalnode_label}])
	parnode_label1,pargraph1 = returngraph(parents[0],graph)
	parnode_label2,pargraph2 = returngraph(parents[1],graph)
	initialvaluelist1,w,wv,tottime=interpreter(parnode_label1,pargraph1, tottime)
	initialvaluelist2,w,wv,tottime=interpreter(parnode_label2,pargraph2, tottime)
	#print('parnode_label2:', parents[1])
	try:
		currentvaluelist = list(zip(initialvaluelist1,initialvaluelist2))
	except Exception as e:
		raise combinatorruntimeerror([{'message':"Unable to zip ouptut of parentnode1 and parentnode2! The output of parentnode1 and parentnode2 should be of list or string type.",'error':repr(e),'nodeid':terminalnode_label}])
	currentvaluelist = [ [i,j] for i,j in currentvaluelist]
	setval_graph('dat',currentvaluelist,graph,terminalnode_label,'N')
	setval_graph('wv',wv,graph,terminalnode_label,'N')
	setval_graph('w',w,graph,terminalnode_label,'N')
	return tottime	
	

def _interpret_agg(nodename,terminalnode_label,graph,tottime):
	try:
		parents = getval_graph(graph,terminalnode_label,'E')
	except Exception as e:
		raise combinatorruntimeerror([{'message':"Unable to get parent nodes of this aggregator node! Please check for input port connections.",'error':repr(e),'nodeid':terminalnode_label}])
	if len(parents) < 2:
		raise combinatorruntimeerror([{'message':"Unable to get all parent nodes of this aggregator node! Please check for all input port connections.",'error':'unconnected input ports','nodeid':terminalnode_label}])
	parnode_label1,pargraph1 = returngraph(parents[0],graph)
	parnode_label2,pargraph2 = returngraph(parents[1],graph)
	
	in_function,w,wv,tottime=interpreter(parnode_label1,pargraph1, tottime)
	initialvaluelist,w,wv,tottime=interpreter(parnode_label2,pargraph2, tottime)
	#print('parnode_label2:', parents[1])
	initialnode = parents[1]
	#print(in_function)
	try:
		iter(initialvaluelist)
	except Exception as e:
		raise combinatorruntimeerror([{'message':"Unable to iterate ouptut of parentnode2! The output of parentnode2 should be of list or string type.",'error':repr(e),'nodeid':terminalnode_label}])
	if not initialvaluelist:
		raise combinatorruntimeerror([{'message':"Output of parentnode2 cannot be empty list!",'error':repr(e),'nodeid':terminalnode_label}])
	if initialvaluelist:
		if len(initialvaluelist) > 1:
			currentvalue1 = initialvaluelist[0]
			currentvalue2 = initialvaluelist[1]
			restofthelist = initialvaluelist[2:]
		else:
			currentvalue1 = initialvaluelist[0]
			currentvalue2 = initialvaluelist[0]
			restofthelist = []
			
		for i in range(len(restofthelist)+1):
			new_in_function = pickle.loads(pickle.dumps(in_function,-1))
			newvaluenode1 = createnode(graph,'K',currentvalue1)
			setval_graph('uex',0,graph,newvaluenode1,'N')
			addlink(graph,newvaluenode1,initialnode)
			del graph['terminalnodes'][newvaluenode1]
			newvaluenode2 = createnode(graph,'K',currentvalue2)
			setval_graph('uex',0,graph,newvaluenode2,'N')
			addlink(graph,newvaluenode2,initialnode)
			del graph['terminalnodes'][newvaluenode2]
			_nlabel0=createnode(graph,'gp',new_in_function)
			setval_graph('uex',0,graph,_nlabel0,'N')
			addlink(graph,_nlabel0,newvaluenode1,newvaluenode2)
			del graph['terminalnodes'][_nlabel0]
		######## point parent graphs of all gp nodes within  in_function to in_function, which are by default pointing to graph
			for nodelabel,node in new_in_function['nodes'].items():
			#print('nodelabel',nodelabel)           
				if node['nm'] == 'gp':
					node['fun']['par'] = new_in_function  
			try:
				currentdata,w,wv,tottime = interpreter(_nlabel0,graph,tottime)
			except combinatorruntimeerror as e:
				e.error.append({'message':"Error in evaluating subgraph from the output of parentnode1 in the aggregator node on the value "+str(currentvalue2)+"! The subgraph from the output of the parentnode1 should be a valid function that can be applied to aggregate each element of the list output of parentnode2.",'error':'parenterror','nodeid':terminalnode_label})
				raise combinatorruntimeerror(e.error)
			except Exception as e:
				raise combinatorruntimeerror([{'message':"Error in evaluating subgraph of parentnode1 in the aggregator node on the value "+str(currentvalue2)+"!",'error':repr(e),'nodeid':terminalnode_label}])
			currentvalue1 = currentdata
			try:
				currentvalue2 = restofthelist[i]
			except:
				pass
			remove_node(graph,_nlabel0)
			remove_node(graph,newvaluenode1)
			remove_node(graph,newvaluenode2)
	setval_graph('dat',currentdata,graph,terminalnode_label,'N')
	setval_graph('wv',wv,graph,terminalnode_label,'N')
	setval_graph('w',w,graph,terminalnode_label,'N')
	return tottime
	

def _interpret_loop(nodename,terminalnode_label,graph,tottime):
	try:
		parents = getval_graph(graph,terminalnode_label,'E')
	except Exception as e:
		raise combinatorruntimeerror([{'message':"Unable to get parent nodes of this loop node! Please check for input port connections.",'error':repr(e),'nodeid':terminalnode_label}])
	if len(parents) < 2:
		raise combinatorruntimeerror([{'message':"Unable to get all parent nodes of this loop node! Please check for all input port connections.",'error':'unconnected input ports','nodeid':terminalnode_label}])
	parnode_label1,pargraph1 = returngraph(parents[0],graph)
	parnode_label2,pargraph2 = returngraph(parents[1],graph)
	_nlabel1=createnode(graph,'lg')
	setval_graph('uex',0,graph,_nlabel1,'N')
	addlink(graph,_nlabel1,parnode_label1)
	del graph['terminalnodes'][_nlabel1]
	try:
		in_function,w,wv,tottime=interpreter(_nlabel1,pargraph1, tottime)
	except combinatorruntimeerror as e:
		e.error.append({'message':"Error in fetching subgraph of parentnode1 of the loop node!",'error':'parenterror','nodeid':terminalnode_label})
		raise combinatorruntimeerror(e.error)
	except Exception as e:
		raise combinatorruntimeerror([{'message':"Error in fetching subgraph of parentnode1 of the loop node!",'error':repr(e),'nodeid':terminalnode_label}])
	initialvalue,w,wv,tottime=interpreter(parnode_label2,pargraph2, tottime)
	#print('parnode_label2:', parents[1])
	initialnode = parents[1]
	if not isinstance(initialvalue,int):
		raise combinatorruntimeerror([{'message':"Parentnode2 output "+str(initialvalue)+" is not an integer!",'error':"Not an integer",'nodeid':terminalnode_label}])
	#print(in_function)
	prev_node = None
	currentdata = initialvalue
	for i in range(initialvalue):
		new_in_function = pickle.loads(pickle.dumps(in_function,-1))   
		_nlabel0=createnode(graph,'gp',new_in_function)
		setval_graph('uex',0,graph,_nlabel0,'N')
		addlink(graph,_nlabel0,initialnode)
		del graph['terminalnodes'][_nlabel0]
		######## point parent graphs of all gp nodes within  in_function to in_function, which are by default pointing to graph
		for nodelabel,node in new_in_function['nodes'].items():
			#print('nodelabel',nodelabel)           
			if node['nm'] == 'gp':
				node['fun']['par'] = new_in_function
		try:
			currentdata,w,wv,tottime = interpreter(_nlabel0,graph,tottime)
		except combinatorruntimeerror as e:
			e.error.append({'message':"Error in evaluating subgraph of parentnode1 on the value "+str(currentdata)+"! The subgraph corresponding to the parentnode1 should be a valid function that can be applied on output of parentnode2 and output of itself.",'error':'parenterror','nodeid':terminalnode_label})
			raise combinatorruntimeerror(e.error)
		except Exception as e:
			raise combinatorruntimeerror([{'message':"Error in evaluating subgraph of parentnode1 in the loop node on the value "+str(currentdata)+"!",'error':repr(e),'nodeid':terminalnode_label}])
		initialnode = _nlabel0
		if prev_node != None:
			#print('prev_node',prev_node)
			remove_node(graph,prev_node)
		prev_node = _nlabel0
	remove_node(graph,prev_node)
	remove_node(graph,_nlabel1)
	setval_graph('dat',currentdata,graph,terminalnode_label,'N')
	setval_graph('wv',wv,graph,terminalnode_label,'N')
	setval_graph('w',w,graph,terminalnode_label,'N')
	return tottime
		
def _interpret_rc(nodename,terminalnode_label,graph,tottime): ###### recursion
	try:
		parents = getval_graph(graph,terminalnode_label,'E')
	except Exception as e:
		raise combinatorruntimeerror([{'message':"Unable to get parent nodes of this recurse node! Please check for input port connections.",'error':repr(e),'nodeid':terminalnode_label}])
	if len(parents) < 3:
		raise combinatorruntimeerror([{'message':"Unable to get all parent nodes of this recurse node! Please check for all input port connections.",'error':'unconnected input ports','nodeid':terminalnode_label}])
	parnode_label,pargraph = returngraph(parents[1],graph)
	stopcondition,w,wv,tottime=interpreter(parnode_label,pargraph, tottime)
	initialnode = parents[2]
	prev_nlabel = -1
	prev_nlabel1 = -1
	while True:
		new_stopcondition = pickle.loads(pickle.dumps(stopcondition,-1))
		_nlabel0=createnode(graph,'gp',new_stopcondition)
		setval_graph('uex',0,graph,_nlabel0,'N')
		addlink(graph,_nlabel0,initialnode)
		del graph['terminalnodes'][_nlabel0]
		######## point parent graphs of all gp nodes within  in_function to in_function, which are by default pointing to graph
		for nodelabel,node in new_stopcondition['nodes'].items():
			#print('nodelabel',nodelabel)           
			if node['nm'] == 'gp':
				node['fun']['par'] = new_stopcondition  
		try:
			currentdata,w,wv,tottime = interpreter(_nlabel0,graph,tottime)
		except combinatorruntimeerror as e:
			try:
				message = "Error in evaluating stopping condition subgraph from the output of parentnode2 on the value "+str(currentdata)+ " in the recurse node! The subgraph corresponding to the parentnode2 should be a valid function that can be applied on output of parentnode3 and evaluated output of the subgraph recieved from parentnode1."
			except:
				message = "Error in evaluating stopping condition subgraph from the output of parentnode2 in the recurse node! The subgraph corresponding to the parentnode2 should be a valid function that can be applied on output of parentnode3 and evaluated output of the subgraph recieved from parentnode1."
			e.error.append({'message':message,'error':'parenterror','nodeid':terminalnode_label})
			raise combinatorruntimeerror(e.error)
		except Exception as e:
			try:
				message = "Error in evaluating stopping condition subgraph from the output of parentnode2 in the recurse node on the value "+str(currentdata)+"!"
			except:
				message = "Error in evaluating stopping condition subgraph from the output of parentnode2 in the recurse node!"
			raise combinatorruntimeerror([{'message':message,'error':repr(e),'nodeid':terminalnode_label}])
		if currentdata:
			parnode_label,pargraph = returngraph(initialnode,graph)
			try:
				data,w1,wv1,tottime = interpreter(parnode_label,pargraph,tottime)
			except combinatorruntimeerror as e:
				try:
					message = "Error in evaluating subgraph from the output of parentnode1 on the value "+str(currentoutput)+ " in the recurse node! The subgraph corresponding to the parentnode1 should be a valid function that can be applied on output of parentnode3 and output of itself."
				except:
					message = "Error in evaluating subgraph from the output of parentnode1 in the recurse node! The subgraph corresponding to the parentnode1 should be a valid function that can be applied on output of parentnode3 and output of itself."
				e.error.append({'message':message,'error':'parenterror','nodeid':terminalnode_label})
				raise combinatorruntimeerror(e.error)
			except Exception as e:
				raise combinatorruntimeerror([{'message':"Error in evaluating subgraph from the output of parentnode1 in the recurse node on the value "+str(currentoutput)+"!",'error':repr(e),'nodeid':terminalnode_label}])
			setval_graph('dat',data,graph,terminalnode_label,'N')
			setval_graph('wv',max(wv,wv1),graph,terminalnode_label,'N')
			setval_graph('w',w1,graph,terminalnode_label,'N')
			return tottime
		else:
			parnode_label,pargraph = returngraph(parents[0],graph)
			function1,w2,wv2,tottime = interpreter(parnode_label,pargraph,tottime)
			_nlabel1=createnode(graph,'wm')
			setval_graph('uex',0,graph,_nlabel1,'N')
			addlink(graph,_nlabel1,initialnode,_nlabel0)
			del graph['terminalnodes'][_nlabel1]
			_nlabel=createnode(graph,'gp',function1)
			setval_graph('uex',0,graph,_nlabel,'N')
			addlink(graph,_nlabel,_nlabel1)
			del graph['terminalnodes'][_nlabel]
			######## point parent graphs of all gp nodes within  in_function to in_function, which are by default pointing to graph
			for nodelabel,node in function1['nodes'].items():
			#print('nodelabel',nodelabel)           
				if node['nm'] == 'gp':
					node['fun']['par'] = function1  
			try:
				currentoutput,w2,wv2,tottime = interpreter(_nlabel,graph,tottime)
			except combinatorruntimeerror as e:
				try:
					message = "Error in evaluating subgraph from the output of parentnode1 on the value "+str(currentoutput)+ " in the recurse node! The subgraph corresponding to the parentnode1 should be a valid function that can be applied on output of parentnode3 and output of itself."
				except:
					message = "Error in evaluating subgraph from the output of parentnode1 in the recurse node! The subgraph corresponding to the parentnode1 should be a valid function that can be applied on output of parentnode3 and output of itself."
				e.error.append({'message':message,'error':'parenterror','nodeid':terminalnode_label})
				raise combinatorruntimeerror(e.error)
			except Exception as e:
				raise combinatorruntimeerror([{'message':"Error in evaluating subgraph from the output of parentnode1 in the recurse node!",'error':repr(e),'nodeid':terminalnode_label}])
			remove_node(graph,prev_nlabel1)
			remove_node(graph,prev_nlabel)
			remove_node(graph,_nlabel0)
			prev_nlabel = _nlabel
			prev_nlabel1 = _nlabel1
			initialnode = _nlabel					
						
						
def _interpreter( terminalnode_label,  graph, tottime):
	global no_of_args
	tottime.consume_time(1)   
	if tottime.get_time() < 1:
		raise time_exception ('time over')
	nodename = getval_graph(graph,terminalnode_label,'N','nm')
	if getval_graph(graph,terminalnode_label,'N','dat') == None:
		if nodename == 'iW': ########### initWorld
			setval_graph('dat',0,graph,terminalnode_label,'N')
			wversion = graph['nodes'][terminalnode_label]['w'].version
			setval_graph('wv',wversion,graph,terminalnode_label,'N')
		elif nodename == 'lg':
			tottime = _interpret_lg(nodename,terminalnode_label,graph,tottime)
		elif nodename == 'gp':
			tottime = _interpret_gp(nodename,terminalnode_label,graph, tottime)
		elif nodename == 'ap':
			tottime = _interpret_ap(nodename,terminalnode_label,graph,tottime)
		elif nodename == 'lp':
			tottime = _interpret_loop(nodename,terminalnode_label,graph,tottime)
		elif nodename == 'fm':
			tottime = _interpret_fmap(nodename,terminalnode_label,graph,tottime)
		elif nodename == 'zp':
			tottime = _interpret_zip(nodename,terminalnode_label,graph,tottime)
		elif nodename == 'ag':
			tottime = _interpret_agg(nodename,terminalnode_label,graph,tottime)
		elif no_of_args[nodename] == 3: #nodename == 'if' or nodename == 'rc' or nodename == 'zp':#nodename in ['if','rc','zp']:
			if nodename == 'if':
				tottime = _interpret_if(nodename,terminalnode_label,graph,tottime)
			elif nodename == 'rc':
				tottime = _interpret_rc(nodename,terminalnode_label,graph,tottime)
			elif nodename == 'ak':
				tottime = _interpret_ak(nodename,terminalnode_label,graph,tottime)
		elif no_of_args[nodename] == 1:#nodename =='K' or nodename == 'id' or nodename == '!' or nodename == 'hd' or nodename == 'tl' or nodename == 'sn' or nodename == 'ac' or nodename == 'gc' or nodename =='nl': #nodename in ['K','id','!','hd','tl','sn','ac','gc','nl']: ########### constant, identity, negate
			tottime = _interpret_single_input_funct(nodename,terminalnode_label,graph,tottime)
		elif no_of_args[nodename] == 2: #nodename == '+' or nodename =='-' or nodename == '*' or nodename == '/' or nodename == '^' or nodename == '&' or nodename == '|' or nodename == '>' or nodename =='=' or nodename =='cn' or nodename =='wm':#nodename == ['+','-','*','/','^','&','|','>','=','cn','wm']: ########### num operators
			tottime = _interpret_two_port_funct(nodename,terminalnode_label,graph,tottime)

		setval_graph('es',1,graph,terminalnode_label,'N')

		#update_program_expression(terminalnode_label,getval_graph(graph,terminalnode_label,'N','nm'),getval_graph(graph,terminalnode_label,'N','dat'), graph)
		update_node_type(graph,terminalnode_label)
	return (pickle.loads(pickle.dumps(graph['nodes'][terminalnode_label]['dat'],-1)),graph['nodes'][terminalnode_label]['w'],graph['nodes'][terminalnode_label]['wv'], tottime)


def interpreter(terminalnode_label, graph,tottime):
	nodename=getval_graph(graph,terminalnode_label,'N','nm')
	if nodename != 'iW' and nodename != 'lg' and getval_graph(graph,terminalnode_label,'N','dat') == None and nodename != 'lp' and nodename != 'fm' and  nodename != 'if':    
		while True:
			_cur_graph = graph
			try:
				parents=_cur_graph['edges'][terminalnode_label]
			except Exception as e:
				raise combinatorruntimeerror([{'message':"Unable to get parent nodes of this node! Please check for all input port connections.",'error':repr(e),'nodeid':terminalnode_label}])
			childnode_label = terminalnode_label
			_prev_graph = _cur_graph
			while True:
				all_parents_executed = 1
				for port,parent_label in parents.items(): ###### iterate all parents
					
					parent_label,_new_cur_graph= returngraph(parent_label,_cur_graph)  ####### _cur_graph can get changed
					if _new_cur_graph['nodes'][parent_label]['nm'] not in ('iW','lg') and _new_cur_graph['nodes'][parent_label]['es'] == 0: ### parent is not executed
						try:
							parents = _new_cur_graph['edges'][parent_label]
						except Exception as e:
							raise combinatorruntimeerror([{'message':"Unable to get parent nodes of this node! Please check for all input port connections.",'error':repr(e),'nodeid':parent_label}])
						childnode_label = parent_label
						all_parents_executed = 0
						_prev_graph = _new_cur_graph
						break
				if 	all_parents_executed == 1 or _prev_graph['nodes'][childnode_label]['nm'] in ['lg', 'if','iW','lp','fm']:
					break
			########### execute child node
			output = _interpreter(childnode_label,_prev_graph,tottime)
			if childnode_label == terminalnode_label and _prev_graph['attr']['label'] == graph['attr']['label']:
				return output
					
	else:
		return _interpreter(terminalnode_label,graph,tottime)	
	
def runp(terminalnode, graph,remoteserviceheader={},time_limit = float("inf")):
	tottime = time_object(time_limit)
	tottime.remoteserviceheader = remoteserviceheader
	data,w,wv,tottime = interpreter(terminalnode,graph,tottime)
	return (data,w,wv,tottime.get_time())