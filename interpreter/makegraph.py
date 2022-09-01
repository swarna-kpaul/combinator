from interpreter.program_expression import *
from interpreter.program_probability import *
import numpy as np
import pickle
label =0
no_of_arguments=0 
world_version=0 
exec_status=0 
update_exp=1 
is_initial=0
equivalent_prog=0 
runtime=0
program_probability=0
reward=0.0
average_reward = (0,0,0)
#init_node_label = 1
graph_label = 1
world = None

class current_node_label:
	def __init__(self):
		self.init_node_label = 1
	
	def set_node_label(self,node_label):
		self.init_node_label = node_label
	
	def inc_node_label(self):
		self.init_node_label += 1

current_node_label_obj = current_node_label()

node_attributes = {'wv': world_version, 'es': exec_status,'uex':update_exp, 'ii':is_initial,'ep':equivalent_prog, 'rt':runtime,'pp':program_probability,'R': reward,'aR': average_reward,'w':world,'ty':None, 'dat':None,'pex':{'data':None, 'world':None},'pint':dict(), 'ni': None, 'fp':{},'pos':{}}
######## pint -> {'nodelabel':{'childnode_index':{'childnode_port':[probability]}}}
######### fp -> {'parentnodelabel'+'-'+'childnodelabel'+'-'+childnode_port: [probability]}}} 

graph_attributes = {'label':0,'name':'graph'}
#nodes = {init_node_label:node_attributes}
#graph = {'edges':{init_node_label:{1:init_node_label,2:init_node_label}}, 'terminalnodes':[terminal_init_node_labels], initialnodes:[initial_init_node_labels]}
#nodes = dict()

initgraph = {'attr':graph_attributes,'world':None,'edges':{},'nodes':{},'terminalnodes':{}, 'initialnodes':[], 'existingnodes':{} ,'atype': {'fun':{'i':['none'],'o':['none']}}}

probability_list={}


def setval_graph(key,val,graph,node_label,property):
	if property == 'N': ######### node
		graph['nodes'][node_label][key] = val
	elif property == 'E': ######## edges
		graph['edges'][node_label][key] = val
		
def getval_graph(graph,node_label,property,*key):
	if property == 'N': ######### node
		if key:
			return (graph['nodes'][node_label][key[0]])
		else:
			return (graph['nodes'][node_label])
	elif property == 'E': ######## edges
		if key:
			return (graph['edges'][node_label][key[0]])
		else:
			return (graph['edges'][node_label])
			
def remove_node(graph,node_label):
	try:       
		del graph['nodes'][node_label]
	except Exception as e:   
		pass
	try:
		del graph['edges'][node_label]
	except Exception as e:   
		pass
	try:
		del graph['terminalnodes'][node_label]
	except Exception as e:   
		pass
	try:
		deledges = [child for child,parents in graph['edges'].items() if node_label in list(parents.values())]
		for nlabel in deledges:
			del graph['edges'][nlabel]
	except Exception as e:   
		pass
		
def update_program_expression(node_label,node_name,node_output, graph):
##### Derive, reduce and update program expression of the program having this node as terminal node 
	if getval_graph(graph,node_label,'N','uex') == 1:
		current_expression = get_program_expression(node_label,node_name,node_output, graph)
		if current_expression:
			if str(current_expression['data']) == 'True' :
				current_expression['data'] = True
			elif str(current_expression['data']) == 'False':
				current_expression['data'] = False
			setval_graph('pex',current_expression,graph,node_label,'N')

def createnode_from_corpus(graph,index):
	global corpusInstance #corpus_of_all_objects
	object = corpusInstance.corpus_of_all_objects[index]
	if 'param' in object:
		_nlabel = createnode( graph,object['nm'],object['param'])
		setval_graph('ty',pickle.loads(pickle.dumps(object['typ'],-1)),graph,_nlabel,'N')
	else:
		_nlabel = createnode( graph,object['nm'])
	setval_graph('ni',index,graph,_nlabel,'N')
	setval_graph('pint',pickle.loads(pickle.dumps(corpusInstance.type_compatible_node_links[index],-1)),graph,_nlabel,'N')
	
	return (_nlabel)


def createnode( graph, nodename,*args):
	global current_node_label_obj,node_attributes, atype, no_of_args
	init_node_label = current_node_label_obj.init_node_label
	graph['nodes'][init_node_label]=pickle.loads(pickle.dumps(node_attributes,-1))
	#graph['initialnodes'].append(init_node_label)
	graph['nodes'][init_node_label]['nm'] = nodename
	if nodename == 'iW':
		graph['nodes'][init_node_label]['w'] = args[0]
		graph['nodes'][init_node_label]['es'] = 1
		graph['nodes'][init_node_label]['ii'] = 1
		graph['nodes'][init_node_label]['pp'] = 1
		graph['world'] = args[0]
	elif nodename == 'K':
		graph['nodes'][init_node_label]['K'] = args[0]
		graph['nodes'][init_node_label]['ty'] = pickle.loads(pickle.dumps(atype['K'],-1))
	elif nodename == 'sn':
		graph['nodes'][init_node_label]['ty'] = pickle.loads(pickle.dumps(atype['sn'],-1))
		graph['nodes'][init_node_label]['ty']['fun']['o'] = args[0]
	elif nodename == 'ac':
		graph['nodes'][init_node_label]['ty'] = pickle.loads(pickle.dumps(atype['ac'],-1))
		graph['nodes'][init_node_label]['ty']['fun']['i'] = args[0]	
	elif nodename in ['id','hd','cn','ap','ag','zp','fm','rc','wm','lg','if','lp','pt']:
		graph['nodes'][init_node_label]['ty'] = pickle.loads(pickle.dumps(atype[nodename],-1))
	elif nodename == 'gp': #composite graph
		fun = args[0]
		
		for k,_n in fun['nodes'].items():
			fun['nodes'][k]['uex'] = 0            
		fun['par'] = graph        
		no_args = 0
		for label in fun['initialnodes']:
			no_args += no_of_args[fun['nodes'][label]['nm']]
		graph['nodes'][init_node_label]['fun'] = fun
		graph['nodes'][init_node_label]['args'] = no_args
		graph['nodes'][init_node_label]['ty'] = fun['atype']
		graph['nodes'][init_node_label]['fname'] = fun['attr']['name']

	label = init_node_label        
	current_node_label_obj.inc_node_label()
	return (label)
	
def creategraph():
	global initgraph, graph_label
	newgraph = pickle.loads(pickle.dumps(initgraph,-1))
	newgraph['attr']['label'] = graph_label
	graph_label +=1
	return (newgraph)

def getargs(nodelabel,graph):
	global no_of_args
	if graph['nodes'][nodelabel]['nm'] == 'gp':
		return (graph['nodes'][nodelabel]['args'])
	else:
		return (no_of_args[graph['nodes'][nodelabel]['nm']])
    
    
def addlink_sub1(graph,nodelabel):
	graph['initialnodes'].append(nodelabel)
	graph['atype']['fun']['i'] += getatype(graph,nodelabel)['fun']['i']
	graph['nodes'][nodelabel]['fp'] = {(0,nodelabel,0,):[1.0]}
	for child,edges in graph['edges'].items():
		for port,parentnode in edges.items():
			if nodelabel == parentnode:
				return 1
	graph['terminalnodes'][nodelabel]=1
	

    
def addlink_sub2(graph,nodelabel,links):
	if nodelabel in graph['edges']:
		linkdict = graph['edges'][nodelabel]
		j = len(linkdict)
	else:
		j = 0
		linkdict = dict()
	for i,link in enumerate(links):
		linkdict[i+j] = link
	graph['edges'][nodelabel] = linkdict
		# Remove non terminal nodes
	for item in links:
		try:
			del graph['terminalnodes'][item]
		except:
			pass
	for child,edges in graph['edges'].items():
		for port,parentnode in edges.items():
			if nodelabel == parentnode:
				return 1
	graph['terminalnodes'][nodelabel]=1

def addlink_sub3(graph,nodelabel):
	if graph['nodes'][nodelabel]['nm'] == 'gp' and len(graph['edges'][nodelabel]) >= getargs(nodelabel,graph): ##### composite graph node
		subgraph = graph['nodes'][nodelabel]['fun']
		j=0
		for inodelabel in subgraph['initialnodes']:
			linkdict = dict()
			for i in range(getargs(inodelabel,subgraph)):
				linkdict[i] = (graph['edges'][nodelabel][j],)
				j += 1
			subgraph['edges'][inodelabel] = linkdict    

def addlink(graph,nodelabel,*links):
	
	if len(links) == 0: #and innode.no_of_arguments > 0:
		addlink_sub1(graph,nodelabel)       
	else:
		addlink_sub2(graph,nodelabel,links)
		addlink_sub3(graph,nodelabel)
	try:
		update_program_expression(nodelabel,graph['nodes'][nodelabel]['nm'],None, graph)
	except:
		pass
		

def resetGraph(graph):
	for label,node in graph['nodes'].items():
		graph['nodes'][label]['dat'] = None
		graph['nodes'][label]['wv'] = 0
		graph['nodes'][label]['R'] = 0
		#graph['nodes'][label]['rt'] = 0
		if graph['nodes'][label]['es'] != 4:
			graph['nodes'][label]['es'] = 0
		if graph['nodes'][label]['nm'] != 'iW':
			graph['nodes'][label]['w'] = None
	for label in graph['initialnodes']:
		graph['nodes'][label]['es'] = 1

######################### Recursive method
def _returnSubgraph(graph,terminalnode_label,subGraph):
	if terminalnode_label in graph['edges'] and graph['nodes'][terminalnode_label]['ii'] !=1 :    
		subGraph['edges'][terminalnode_label] = pickle.loads(pickle.dumps(graph['edges'][terminalnode_label],-1))
		for i,sourcenode_label in graph['edges'][terminalnode_label].items():
			if graph['nodes'][sourcenode_label]['ii'] == 1: #or ( sourcenode_label not in graph['edges'] and no_of_args[graph['nodes'][sourcenode_label]['nm']] >0): ######### sourcenode initialnode
				subGraph['initialnodes'].append(sourcenode_label)
				subGraph = _returnSubgraph(graph,sourcenode_label,subGraph)
			else:
				subGraph = _returnSubgraph(graph,sourcenode_label,subGraph)
	############## copy subgraph node
	subGraph['nodes'][terminalnode_label] = {}
	for key in graph['nodes'][terminalnode_label].keys():
		if key == 'w':
			subGraph['nodes'][terminalnode_label][key] = graph['nodes'][terminalnode_label][key]
		else:
			subGraph['nodes'][terminalnode_label][key] = pickle.loads(pickle.dumps(graph['nodes'][terminalnode_label][key], -1))

	return subGraph
	

	
############################# Non recursive method
# def _returnSubgraph1(subGraph,_terminalnode_label,graph_edges,graph):
	# if _terminalnode_label not in subGraph['edges']: 
		# subGraph['edges'][_terminalnode_label] = pickle.loads(pickle.dumps(graph_edges[_terminalnode_label], -1))
	# for i,sourcenode_label in graph_edges[_terminalnode_label].items():
		# if graph['nodes'][sourcenode_label]['ii'] == 1: # or ( sourcenode_label not in graph['edges'] and no_of_args[graph['nodes'][sourcenode_label]['nm']] >0): ######### sourcenode initialnode
			# subGraph['initialnodes'].append(sourcenode_label)
		# _child_node_label = _terminalnode_label
		# _child_node_port = i                
		# #_terminalnode_label = sourcenode_label              
		# break
	# return (_child_node_label,_child_node_port,sourcenode_label)

# def _returnSubgraph2(subGraph,_terminalnode_label,graph_edges,_child_node_label,_child_node_port,graph,terminalnode_label):
	# subGraph['nodes'][_terminalnode_label] = pickle.loads(pickle.dumps(graph['nodes'][_terminalnode_label], -1))
	# del graph_edges[_child_node_label][_child_node_port]
	# if not graph_edges[_child_node_label]:
		# del graph_edges[_child_node_label]
	# _terminalnode_label = terminalnode_label
	# return _terminalnode_label

# def _returnSubgraph(graph,terminalnode_label,subGraph):
	# graph_edges = pickle.loads(pickle.dumps(graph['edges'],-1))
	# _terminalnode_label = terminalnode_label
	# while True:    
		# if terminalnode_label not in graph_edges:
			# subGraph['nodes'][terminalnode_label] = pickle.loads(pickle.dumps(graph['nodes'][terminalnode_label], -1))         
			# return subGraph
		# if _terminalnode_label in graph_edges:  ######### still needs to be traversed to parent nodes
			# _child_node_label,_child_node_port,_terminalnode_label = _returnSubgraph1(subGraph,_terminalnode_label,graph_edges,graph)
		# else: ##### no parent edges left              
			# _terminalnode_label = _returnSubgraph2(subGraph,_terminalnode_label,graph_edges,_child_node_label,_child_node_port,graph,terminalnode_label)

	
	
def returnSubgraph(graph,terminalnode_label,initialnode_label=None):
	subGraph = creategraph()
	subGraph = _returnSubgraph(graph,terminalnode_label,subGraph) 
	subGraph['terminalnodes'] = {terminalnode_label: 1}
	subGraph['initialnodes'] = list(set(subGraph['initialnodes']))
	world= graph['nodes'][subGraph['initialnodes'][0]]['w']
	wversion = max( graph['nodes'][i]['wv'] for i in subGraph['initialnodes'] )
	if initialnode_label == None:
		temp_node_label=subGraph['initialnodes']
		########## reorder the initial nodes ###############
		sorted_node_label_idx = sorted(range(len(temp_node_label)),key=temp_node_label.__getitem__)
		subGraph['initialnodes'] =[subGraph['initialnodes'][j] for j in sorted_node_label_idx]
		i_type = []
		for nodelabel in subGraph['initialnodes']:
			i_type += getatype(subGraph,nodelabel)['fun']['i']
	else: ########### replace initialnodes with initialnode
		initialnode_i_type = 'any'
		prev_initialnode_i_type = 'any'
		for term_node,_edges in subGraph['edges'].items():
			for term_nodeport,sourcenode_label in _edges.items():
				if sourcenode_label in subGraph['initialnodes']:
				#################### check type compatibility: all child node ports connecting initialnodes should have same type
					initialnode_i_type = getatype(subGraph,term_node)['fun']['i'][term_nodeport]                  
					if prev_initialnode_i_type != initialnode_i_type and initialnode_i_type != 'any' and prev_initialnode_i_type != 'any':
						raise Exception("Disparate node input types in return subgraph")
					elif initialnode_i_type == 'any':
						pass
					else:
						prev_initialnode_i_type = initialnode_i_type
					subGraph['edges'][term_node][term_nodeport] = initialnode_label
					try:
						del subGraph['nodes'][sourcenode_label]
					except:
						pass
					############ point gp nodes functions initial nodes to parent graph initial node
					if subGraph['nodes'][term_node]['nm'] == 'gp':
						for initnodeid in subGraph['nodes'][term_node]['fun']['initialnodes']:
							initialedges = subGraph['nodes'][term_node]['fun']['edges'][initnodeid]
							for port,initialedge in initialedges.items():
								if initialedge == (sourcenode_label,) :
									subGraph['nodes'][term_node]['fun']['edges'][initnodeid][port] = (initialnode_label,)
		i_type = [prev_initialnode_i_type]

		subGraph['initialnodes'] = [initialnode_label]
		subGraph['nodes'][initialnode_label] = pickle.loads(pickle.dumps(graph['nodes'][initialnode_label], -1))
		subGraph['nodes'][initialnode_label]['ii'] = 1
	for nodelabel,node in subGraph['nodes'].items():
			#print('nodelabel',nodelabel)           
		if node['nm'] == 'gp':
			node['fun']['par'] = subGraph	
	############### set atype
	subGraph['atype']= {'fun':{'i':i_type, 'o': getatype(subGraph,terminalnode_label)['fun']['o']}}
	return (subGraph, world,wversion )