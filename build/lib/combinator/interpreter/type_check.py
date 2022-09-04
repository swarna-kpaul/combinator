from combinator.interpreter.globalobjects  import *

def _getatype(graph,nodelabel):
	global atype
	nodetype = graph['nodes'][nodelabel]['ty']
	if nodetype == None:
		nodetype = atype[graph['nodes'][nodelabel]['nm']]
	return nodetype #pickle.loads(pickle.dumps(nodetype,-1))
	
def getatype(graph,nodelabel):
	if isinstance(nodelabel, tuple):
		nodetype = _getatype(graph['par'],nodelabel[0])
	else:
		nodetype = _getatype(graph,nodelabel)
	return nodetype        
	
def getatype_from_index(node_index):
	global corpusInstance, atype #, corpus_of_all_objects
	if 'typ' in corpusInstance.corpus_of_all_objects[node_index]:
		outputtype = corpusInstance.corpus_of_all_objects[node_index]['typ']
	else:
		outputtype = atype[corpusInstance.corpus_of_all_objects[node_index]['nm']]
	return outputtype

def check_type_compatibility(parentnode_index,childnode_index,childnode_port,flag,*graph): ## flag 0 = parent and child from index, flag 1 = parent from graph and child from index, flag 2 = parent from index and child from graph, flag 3 = parent from index and child from index
	global corpusInstance, atype #, corpus_of_all_objects
	if not graph:
		parentnode_outputtype = getatype_from_index(parentnode_index)['fun']['o'][0]
		childnode_inputtype = getatype_from_index(childnode_index)['fun']['i'][childnode_port]
		parentnm = corpusInstance.corpus_of_all_objects[parentnode_index]['nm']
		childnm =  corpusInstance.corpus_of_all_objects[childnode_index]['nm']       
	elif flag == 1:
		graph = graph[0]
		parentnode_outputtype = getatype(graph,parentnode_index)['fun']['o'][0]
		childnode_inputtype = getatype_from_index(childnode_index)['fun']['i'][childnode_port]
		parentnm = graph['nodes'][parentnode_index]['nm']
		childnm =  corpusInstance.corpus_of_all_objects[childnode_index]['nm'] 
	elif flag == 2:
		graph = graph[0]
		parentnode_outputtype = getatype_from_index(parentnode_index)['fun']['o'][0]
		childnode_inputtype = getatype(graph,childnode_index)['fun']['o'][0]
		parentnm = corpusInstance.corpus_of_all_objects[parentnode_index]['nm']
		childnm =  graph['nodes'][childnode_index]['nm']
	elif flag == 3:
		graph = graph[0]
		parentnode_outputtype = getatype(graph,parentnode_index)['fun']['o'][0]
		childnode_inputtype = getatype(graph,childnode_index)['fun']['o'][0]
		parentnm = graph['nodes'][parentnode_index]['nm']
		childnm =  graph['nodes'][childnode_index]['nm']       
	if (parentnode_outputtype == 'world' or childnode_inputtype ==  'world') and parentnode_outputtype != childnode_inputtype:
		return 0
	elif childnm == 'lg' and parentnm == 'lg': ########## 2 end to end lg not allowed
		return 0
	elif childnm == 'K' and parentnm not in ('sn','ap','rc','iW','id','if','lp'):
		return 0
	elif childnm == 'rc' and   childnode_port in (0,1,) and parentnm == 'iW':
		return 0        
	elif childnm == 'rc' and childnode_port == 1 and isinstance(parentnode_outputtype, dict):
		if parentnode_outputtype['fun']['o'][0] in ('any','bool','fun',):
			return 1
		else:
			return 0 
	elif childnm == 'rc' and childnode_port == 0 and isinstance(parentnode_outputtype, dict):
		if parentnode_outputtype['fun']['o'][0] != parentnode_outputtype['fun']['i'][0] and parentnode_outputtype['fun']['i'][0]  not in ('any','fun',) and parentnode_outputtype['fun']['o'][0]  not in ('any','fun',):
			return 0
		else:
			return 1
	elif parentnode_outputtype == 'any' or childnode_inputtype == 'any' or parentnode_outputtype == childnode_inputtype or (childnode_inputtype == 'fun' and 'fun' in parentnode_outputtype):
		return 1 ###### compatible     
	else:
		return 0 ##### not compatioble

    
def check_parent_group_compatibility_test(parentnodes,childnode_index,graph):
	global corpusInstance,atype #, corpus_of_all_objects
	childnm =  corpusInstance.corpus_of_all_objects[childnode_index]['nm'] 
	if childnm == 'rc':
			#if  #parentnodes[0] == parentnodes[1] or 
			if parentnodes[0] == parentnodes[2] or   parentnodes[1] == parentnodes[2]:
				return 0
	return 1
		
def check_parent_group_compatibility(parentnodes,childnode_index,graph):
	global corpusInstance,atype #, corpus_of_all_objects
	childnm =  corpusInstance.corpus_of_all_objects[childnode_index]['nm'] 
	if childnm == 'rc':
		_check_result = 1
		parent1_atype = getatype(graph,parentnodes[0])
		parent2_atype = getatype(graph,parentnodes[1])
		parent3_atype = getatype(graph,parentnodes[0])
		if isinstance(parent1_atype,dict):
			if parent1_atype['fun']['i'][0] != parent3_atype and parent3_atype not in ('any','fun',) and parent1_atype['fun']['i'][0] not in ('any','fun',):
				return 0
		if isinstance(parent2_atype,dict):
			if parent2_atype['fun']['i'][0] != parent3_atype and parent3_atype not in ('any','fun') and parent2_atype['fun']['i'][0] not in ('any','fun',):
				return 0
	return 1
		
def is_number(n):
    try:
        float(n)   # Type-casting the string to `float`.
                   # If string is not a valid `float`, 
                   # it'll raise `ValueError` exception
    except:
        return False
    return True

def is_char(n):
    try:
        n.isalpha()   # Type-casting the string to `float`.
                   # If string is not a valid `float`, 
                   # it'll raise `ValueError` exception
    except:
        return False
    return True
		
def get_data_type(val):
	if is_char(val):
		return ('char')
	elif is_number(val):
		return('num')
	elif type(val) == type(True) or type(val) == type(False):
		return('bool')
	elif isinstance(val,dict):
		return ('fun')
	elif isinstance(val,list):
		return('list')
	else:
		return('any')

def update_node_type(graph,node_label):
	if graph['nodes'][node_label]['nm'] == 'id':
		parent_nodelabel = graph['edges'][node_label][0]
		parent_atype = getatype(graph,parent_nodelabel)
		if parent_atype['fun']['o'][0] != 'any':
			graph['nodes'][node_label]['ty']['fun']['i'][0]=parent_atype['fun']['o'][0]
			graph['nodes'][node_label]['ty']['fun']['o'][0] = graph['nodes'][node_label]['ty']['fun']['i'][0]
	elif graph['nodes'][node_label]['nm'] == 'if':
		parent0_nodelabel = graph['edges'][node_label][0]
		if graph['nodes'][parent0_nodelabel]['dat']:
			graph['nodes'][node_label]['ty'] = {'fun':{'i':'any','o':getatype(graph,graph['edges'][node_label][1])['fun']['o']}}
		else:          
			graph['nodes'][node_label]['ty'] = {'fun':{'i':'any','o':getatype(graph,graph['edges'][node_label][2])['fun']['o']}}
	elif graph['nodes'][node_label]['nm'] == 'hd':
		graph['nodes'][node_label]['ty']['fun']['o'][0] = get_data_type(graph['nodes'][node_label]['dat'])
	elif graph['nodes'][node_label]['nm'] == 'agg':     
		graph['nodes'][node_label]['ty']['fun']['o'][0] = 'any'#innode.links[0].funct()['data'].atype['function']['output']
	elif graph['nodes'][node_label]['nm'] == 'rc':
		graph['nodes'][node_label]['ty']['fun']['o'][0] = get_data_type(graph['nodes'][node_label]['dat']) #innode.links[0].funct()['data'].atype['function']['output']
	elif graph['nodes'][node_label]['nm'] == 'lp':
		graph['nodes'][node_label]['ty']['fun']['o'][0] = get_data_type(graph['nodes'][node_label]['dat'])
	elif graph['nodes'][node_label]['nm'] == 'lg':
		#parent_atype = getatype(graph,graph['edges'][node_label][0])
		graph['nodes'][node_label]['ty']['fun']['o'][0] = graph['nodes'][node_label]['dat']['atype']#get_data_type(graph['nodes'][node_label]['dat'])