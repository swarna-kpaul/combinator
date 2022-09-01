from interpreter.type_check import *

def initialize_probability():
	global corpusInstance,no_of_args #corpus_of_all_objects, corpus_index
	corpus_of_objects = { i: corpusInstance.corpus_of_all_objects[i] for i in corpusInstance.corpus_index}
	##### creating initial type graph
	type_compatible_node_links ={}
	for i_node in corpusInstance.corpus_index:
		type_compatible_node_links[i_node] = dict()
		i_node_childs = 0
		for j_node in corpusInstance.corpus_index:
			if corpusInstance.corpus_of_all_objects[j_node]['nm'] == 'iW':
				continue
			type_compatible_node_links[i_node][j_node] = dict()
			for k_in_links in range(no_of_args[corpusInstance.corpus_of_all_objects[j_node]['nm']]):
				if check_type_compatibility(i_node,j_node,k_in_links,0): #to check for type compatibility 
					type_compatible_node_links[i_node][j_node][k_in_links]=[0]
					i_node_childs +=1
			if not type_compatible_node_links[i_node][j_node]:
				del type_compatible_node_links[i_node][j_node]                
		########## calculating initial probability      
		init_probability = 1/i_node_childs
		for j_node,val in type_compatible_node_links[i_node].items():
			for k_in_links,val1 in val.items():
				type_compatible_node_links[i_node][j_node][k_in_links][0]=init_probability
	
	corpusInstance.update_pint(type_compatible_node_links)
	return (corpus_of_objects)
	

def calculate_total_probability(fp):
	probability =1
	for k,p in fp.items():
		probability *= p[0]
	return probability

    
def sub_fun1(fp, graph,parent_label):
	fp.update( graph['nodes'][parent_label]['fp'])  
    
def sub_fun2( fp,  graph, parent_label,  terminalnode_label,  _port,  childnode_index):
	fp[(parent_label,terminalnode_label,_port,)] = graph['nodes'][parent_label]['pint'][childnode_index][_port]    
    
def get_factored_probability( graph, terminalnode_label, childnode_index, links):
	fp = {}
		#### merge parents factored_probability
	for _port,parent_label in enumerate(links):
		#sub_fun1(fp, graph,parent_label)
		#sub_fun2(fp, graph,parent_label, terminalnode_label, _port, childnode_index)
		fp.update( graph['nodes'][parent_label]['fp'])
		fp[(parent_label,terminalnode_label,_port,)] = graph['nodes'][parent_label]['pint'][childnode_index][_port]
	######## return factored_probability
	return fp
	
