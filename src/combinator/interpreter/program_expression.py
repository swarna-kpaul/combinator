from sympy import Symbol,simplify
from combinator.interpreter.globalobjects import no_of_args


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
		n.isalpha()# Type-casting the string to `float`.
				# If string is not a valid `float`, 
				# it'll raise `ValueError` exception
	except:
		return False
	return True
	
def get_parent_expression(terminalnode_label,graph):
	pex = []
	parents=graph['edges'][terminalnode_label]
	for k,parnode_label in parents.items():
		if isinstance(parnode_label, tuple):
			pex.append(graph['par']['nodes'][parnode_label[0]]['pex'])
		else:
			pex.append(graph['nodes'][parnode_label]['pex'])
	return (pex)
	
		
def get_algebra_expression(terminalnode_label,node_output,node_name,graph):
	pex = get_parent_expression(terminalnode_label,graph)
	parent_expression1 = pex[0]
	parent_expression2 = pex[1]
	if  len(parent_expression1['world']) > len(parent_expression2['world']):
		best_world = parent_expression1['world']
	else:
		best_world = parent_expression2['world']
	parent_expression1 = parent_expression1['data']
	parent_expression2 = parent_expression2['data']
	if is_number(parent_expression1) and is_number(parent_expression2) and node_output !=None:
		current_expression = node_output
	elif node_name == '+':
		current_expression = simplify(parent_expression1+parent_expression2)
	elif node_name == '-':
		current_expression = simplify(parent_expression1-parent_expression2)
	elif node_name == '*':
		current_expression = simplify(parent_expression1*parent_expression2)
	elif node_name == '/':
		current_expression = simplify(parent_expression1/parent_expression2)
	elif node_name == '^':
		current_expression = simplify(parent_expression1**parent_expression2)
		
	return {'data':current_expression,'world':best_world}
	
def get_logical_expression(terminalnode_label,node_output,node_name,graph):
	pex = get_parent_expression(terminalnode_label,graph)
	parent_expression1 = pex[0]
	parent_expression2 = pex[1]
	if  len(parent_expression1['world']) > len(parent_expression2['world']):
		best_world = parent_expression1['world']
	else:
		best_world = parent_expression2['world']
	parent_expression1 = parent_expression1['data']
	parent_expression2 = parent_expression2['data']
	if (('sympy.core' in str(type(parent_expression1)) or 'sympy.core' in str(type(parent_expression2))) and (parent_expression1 not in (True,False) or parent_expression2 not in (True,False)) and (parent_expression1 != parent_expression2)) and node_name == '=':
		current_expression = Symbol(str(parent_expression1)+'='+str(parent_expression2))
	elif parent_expression1 == parent_expression2 and node_name == '=':
		current_expression = True
	elif (('sympy.core' not in str(type(parent_expression1)) and 'sympy.core' not in str(type(parent_expression2))) or (parent_expression1  in (True,False) and parent_expression2 in (True,False))) and node_output !=None:
		current_expression = node_output
	elif node_name == '=':
		current_expression = parent_expression1 == parent_expression2
	elif node_name == '>':
		current_expression = Symbol(str(parent_expression1)+'>'+str(parent_expression2))
	elif node_name == '&':
		current_expression = simplify(parent_expression1 & parent_expression2)
	elif node_name == '|':
		current_expression = simplify(parent_expression1 | parent_expression2)
		
	return {'data':current_expression,'world':best_world}
		
		
		
def get_program_expression(terminalnode_label,node_name,node_output,graph):
	current_expression = dict()
	if 'iW' == node_name :
		current_expression = {'data':0, 'world': 'iW()'}
		
	elif 'K' == node_name :
		parent_expression = get_parent_expression(terminalnode_label,graph)[0]
		if 'fun' in graph['nodes'][terminalnode_label]['ty']['fun']['o'][0]: ## constant returns function
			current_expression = {'data':Symbol(type(graph['nodes'][terminalnode_label]['K']).__name__), 'world':parent_expression['world']}
		else: #### constant returns data
			current_expression = {'data':graph['nodes'][terminalnode_label]['K'], 'world':parent_expression['world']}
	elif 'sn' == node_name:
		parent_expression = get_parent_expression(terminalnode_label,graph)[0]
		new_world = parent_expression['world'] + '.S()'
		current_expression = {'data':Symbol(new_world), 'world': new_world}
	elif 'gc' == node_name:
		parent_expression = get_parent_expression(terminalnode_label,graph)[0]
		new_world = parent_expression['world'] + '.GC()'
		current_expression = {'data':Symbol(new_world), 'world': new_world}
	elif 'ac' == node_name:
		parent_expression = get_parent_expression(terminalnode_label,graph)[0]
		new_world = '{{'+parent_expression['world'] + '}X{'+str(parent_expression['data'])+'}}.A()'
		current_expression = {'data':Symbol(new_world), 'world': new_world}
	elif node_name in ('id','pt'):
		parent_expression = get_parent_expression(terminalnode_label,graph)[0]
		current_expression = parent_expression
	elif node_name == '+' or node_name == '-' or node_name == '*' or node_name == '/' or node_name == '^':
		current_expression = get_algebra_expression(terminalnode_label,node_output,node_name,graph)
	elif node_name == '=' or node_name == '>' or node_name == '&' or node_name == '|':
		current_expression = get_logical_expression(terminalnode_label,node_output,node_name,graph)
	elif node_name == '!':
		parent_expression = get_parent_expression(terminalnode_label,graph)[0]
		if parent_expression['data'] in (True,False) and node_output !=None:
			current_expression = {'data':node_output,'world':parent_expression['world']}
		else:
			current_expression = {'data':simplify(~parent_expression['data']),'world':parent_expression['world']}
	elif node_name == 'if':
		pex = get_parent_expression(terminalnode_label,graph)
		parent_expression1 = pex[0]
		parent_expression2 = pex[1]
		parent_expression3 = pex[2]		 
			
		if parent_expression1['data'] == True:
			if  len(parent_expression1['world']) > len(parent_expression2['world']):
				best_world = parent_expression1['world']
			else:
				best_world = parent_expression2['world']
			current_expression = {'data':parent_expression2['data'],'world':best_world}
		elif parent_expression1['data'] == False:
			if  len(parent_expression1['world']) > len(parent_expression3['world']):
				best_world = parent_expression1['world']
			else:
				best_world = parent_expression3['world']
			current_expression = {'data':parent_expression3['data'],'world':best_world}
		else:
			if parent_expression1['world'] == parent_expression2['world'] and parent_expression1['world'] == parent_expression3['world']:
				best_world = parent_expression1['world']
			elif parent_expression1['world'] == parent_expression2['world']:
				best_world = '{'+parent_expression1['world']+'}.sum.{'+ parent_expression3['world']+'}'
			elif parent_expression1['world'] == parent_expression3['world']:
				best_world = '{'+parent_expression1['world']+'}.sum.{'+ parent_expression2['world']+'}'
			elif parent_expression2['world'] == parent_expression3['world']:
				best_world = '{'+parent_expression1['world']+'}.sum.{'+ parent_expression2['world']+'}'
			else:
				best_world = '{'+parent_expression1['world']+'}.sum.{'+ parent_expression2['world']+'}.sum.{'+ parent_expression3['world']+'}'
			current_expression = {'data':Symbol('{{'+str(parent_expression2['data'])+'}.sum.{'+str(parent_expression3['data'])+'}}.{'+ str(parent_expression1['data'])+'}?'),'world':best_world}
			
	elif node_name == 'lg':
		pex = get_parent_expression(terminalnode_label,graph)[0]
		parent_expression = str(pex['data']).replace(" ","").replace("iW()","id()")
		parent_world = str(pex['world']).replace(" ","")
		#if parent_expression[0:4] == 'iW()':
		#	parent_expression = parent_expression[4:]
			#parent_expression = 'iW().'+parent_expression
		parent_expression = '{'+parent_expression+'}.id()'
		current_expression = {'data':Symbol(parent_expression),'world': parent_world}
		
	elif node_name == 'rc':
		pex = get_parent_expression(terminalnode_label,graph)
		parent_expression1 = pex[0]
		parent_expression2 = pex[1]
		parent_expression3 = pex[2]
		if  len(parent_expression1['world']) > max(len(parent_expression2['world']),len(parent_expression3['world'])) :
			best_world = parent_expression1['world']
		elif len(parent_expression2['world']) > max(len(parent_expression1['world']),len(parent_expression3['world'])):
			best_world = parent_expression2['world']
		else:
			best_world = parent_expression3['world']
			
		######## Check if input 1 contains any monadic function
		if 'S()' in str(parent_expression1['data']) or 'A()' in str(parent_expression1['data']) or 'GC()' in str(parent_expression1['data']):
			monadic_in1 = 1
		else:
			monadic_in1 = 0
		######## Check if input 2 contains any monadic function
		if 'S()' in str(parent_expression2['data']) or 'A()' in str(parent_expression2['data']) or 'GC()' in str(parent_expression2['data']):
			monadic_in2 = 1
		else:
			monadic_in2 = 0
		
		######## If input 3 is a function type or any type Check if input 3 contains any monadic function  
		parent2_ty=graph['nodes'][graph['edges'][terminalnode_label][2]]['ty']
		try:
			parent2_ty = parent2_ty['fun']['o']
			if ('fun' in parent2_ty or 'any' in parent2_ty) and ('S()' in str(parent_expression3['data']) or 'A()' in str(parent_expression3['data']) or 'GC()' in str(parent_expression3['data'])):
				monadic_in3 = 1
			else:
				monadic_in3 = 0
		except:
			parent2_ty = None
			monadic_in3 = 0
		
			
		####### if all 3 inputs dont have any monadic functions then the recurse node is side effect free
		if	 monadic_in1 == 0 and monadic_in2 == 0 and monadic_in3 ==0 and node_output !=None:
		#if 'iW()' not in str(parent_expression1['data']) and 'iW()' not in str(parent_expression2['data']) and 'iW()' not in str(parent_expression3['data']): # all three inputs doesn't have any side effects
			current_expression = {'data':node_output,'world':best_world}
		else: # some inputs have effects
			current_data = Symbol('{{'+str(parent_expression1['data'])+'}X{'+str(parent_expression2['data'])+'}X{'+str(parent_expression3['data'])+'}}.recurse()')
			best_world +='.'+(str(current_data))
			current_expression = {'data':current_data,'world':best_world}
			
	elif node_name == 'lp':
		pex = get_parent_expression(terminalnode_label,graph)
		parent_expression1 = pex[0]
		parent_expression2 = pex[1]
		if  len(parent_expression1['world']) > len(parent_expression2['world']):
			best_world = parent_expression1['world']
		else:
			best_world = parent_expression2['world']
		
		######## Check if input 1 contains any monadic function
		if ('S()' in str(parent_expression1['data']) or 'A()' in str(parent_expression1['data']) or 'GC()' in str(parent_expression1['data'])) and node_output !=None:
			current_expression = {'data':node_output,'world':best_world}
		else:
			current_data = Symbol('{{'+str(parent_expression1['data'])+'}X{'+str(parent_expression2['data'])+'}}.loop()')
			best_world +='.'+(str(current_data))
			current_expression = {'data':current_data,'world':best_world}
			
	elif node_name == 'ap':
		pex = get_parent_expression(terminalnode_label,graph)
		parent_expression1 = pex[0]
		parent_expression2 = pex[1]
		if  len(parent_expression1['world']) > len(parent_expression2['world']) :
			best_world = parent_expression1['world']
		else:
			best_world = parent_expression2['world']
		current_data = Symbol('{'+str(parent_expression2['data'])+'}.{'+str(parent_expression1['data'])+'}')
		current_expression = {'data':current_data,'world':best_world}
	
	elif node_name == 'hd':
		parent_expression1 = get_parent_expression(terminalnode_label,graph)[0]
		if isinstance(parent_expression1['data'],list) and node_output !=None:
			current_expression = {'data':node_output,'world':parent_expression1['world']}
		else:
			current_expression = {'data':Symbol('{'+str(parent_expression1['data'])+'}.head()'),'world':parent_expression1['world']}
	elif node_name == 'tl':
		parent_expression1 = get_parent_expression(terminalnode_label,graph)[0]
		if isinstance(parent_expression1['data'],list) and node_output !=None:
			current_expression = {'data':node_output,'world':parent_expression1['world']}
		else:
			current_expression = {'data':Symbol('{'+str(parent_expression1['data'])+'}.tail()'),'world':parent_expression1['world']}
	elif node_name == 'cn':
		pex = get_parent_expression(terminalnode_label,graph)
		parent_expression1 = pex[0]
		parent_expression2 = pex[1]
		if  len(parent_expression1['world']) > len(parent_expression2['world']) :
			best_world = parent_expression1['world']
		else:
			best_world = parent_expression2['world']
		if ('sympy.core' not in str(type(parent_expression1['data'])) and 'sympy.core' not in str(type(parent_expression2['data']))) and node_output !=None:
			current_expression = {'data':node_output,'world':best_world}
		else:
			current_expression = {'data':Symbol('{{'+str(parent_expression1['data'])+'}X{'+str(parent_expression2['data'])+'}}.cons()'),'world':best_world}
		
	elif node_name == 'nl':
		pex = get_parent_expression(terminalnode_label,graph)[0]
		current_expression = {'data':[],'world':pex['world']}
		
	elif node_name == 'pop':
		pex = get_parent_expression(terminalnode_label,graph)
		parent_expression1 = pex[0]
		parent_expression2 = pex[1]
		if  len(parent_expression1['world']) > len(parent_expression2['world']) :
			best_world = parent_expression1['world']
		else:
			best_world = parent_expression2['world']
		if ('sympy.core' not in str(type(parent_expression1['data'])) and 'sympy.core' not in str(type(parent_expression2['data']))) and node_output !=None:
			current_expression = {'data':node_output,'world':best_world}
		else:
			current_expression = {'data':Symbol('{{'+str(parent_expression1['data'])+'}X{'+str(parent_expression2['data'])+'}}.pop()'),'world':best_world}

	elif node_name == 'gp':
		pex = get_parent_expression(terminalnode_label,graph)[0]
		current_expression = {'data':Symbol('{'+str(pex['data'])+'}.gp()'),'world':pex['world']}
		
	elif node_name == 'wm':
		pex = get_parent_expression(terminalnode_label,graph)
		parent_expression1 = pex[0]
		parent_expression2 = pex[1]
		
		if  len(parent_expression1['world']) > len(parent_expression2['world']):
			best_world = parent_expression1['world']
		else:
			best_world = parent_expression2['world']
		if is_char(parent_expression1['data']):
			current_expression = {'data':Symbol(parent_expression1['data']),'world':best_world}
		else:
			current_expression = {'data':parent_expression1['data'],'world':best_world}
	
	elif node_name == 'fm':
		pex = get_parent_expression(terminalnode_label,graph)
		parent_expression1 = pex[0]
		parent_expression2 = pex[1]
		if len(parent_expression1['world']) > len(parent_expression2['world']):
			best_world = parent_expression1['world']
		else:
			best_world = parent_expression2['world']
		if 'S()' in str(parent_expression1['data']) or 'A()' in str(parent_expression1['data']) or 'GC()' in str(parent_expression1['data']):
			monadic_in1 = 1
		else:
			monadic_in1 = 0
		if	 monadic_in1 == 0 and node_output !=None:
			current_expression = {'data':node_output,'world':best_world}
		else:
			current_data = Symbol('{{'+str(parent_expression1['data'])+'}X{'+str(parent_expression2['data'])+'}}.fmap()')
			best_world +='.'+(str(current_data))
			current_expression = {'data':current_data,'world':best_world}
			
	elif node_name == 'ag':
		pex = get_parent_expression(terminalnode_label,graph)
		parent_expression1 = pex[0]
		parent_expression2 = pex[1]
		if len(parent_expression1['world']) > len(parent_expression2['world']):
			best_world = parent_expression1['world']
		else:
			best_world = parent_expression2['world']
		if 'S()' in str(parent_expression1['data']) or 'A()' in str(parent_expression1['data']) or 'GC()' in str(parent_expression1['data']):
			monadic_in1 = 1
		else:
			monadic_in1 = 0
		if	 monadic_in1 == 0 and node_output !=None:
			current_expression = {'data':node_output,'world':best_world}
		else:
			current_data = Symbol('{{'+str(parent_expression1['data'])+'}X{'+str(parent_expression2['data'])+'}}.aggregate()')
			best_world +='.'+(str(current_data))
			current_expression = {'data':current_data,'world':best_world}
	
	elif node_name == 'zp':
		pex = get_parent_expression(terminalnode_label,graph)
		parent_expression1 = pex[0]
		parent_expression2 = pex[1]
		parent_expression2 = pex[2]
		if  len(parent_expression1['world']) > max(len(parent_expression2['world']),len(parent_expression3['world'])) :
			best_world = parent_expression1['world']
		elif len(parent_expression2['world']) > max(len(parent_expression1['world']),len(parent_expression3['world'])):
			best_world = parent_expression2['world']
		else:
			best_world = parent_expression3['world']

		parent2_ty=graph['nodes'][graph['edges'][terminalnode_label][1]]['ty']
		try:
			parent2_ty = parent2_ty['fun']['o']
					######## Check if input 2 contains any monadic function
			if ('fun' in parent2_ty or 'any' in parent2_ty) and 'S()' in str(parent_expression2['data']) or 'A()' in str(parent_expression2['data']) or 'GC()' in str(parent_expression2['data']):
				monadic_in2 = 1
			else:
				monadic_in2 = 0
		except:
			parent2_ty = None
			monadic_in2 = 0
			
		######## Check if input 1 contains any monadic function
		if 'S()' in str(parent_expression1['data']) or 'A()' in str(parent_expression1['data']) or 'GC()' in str(parent_expression1['data']):
			monadic_in1 = 1
		else:
			monadic_in1 = 0

		parent2_ty=graph['nodes'][graph['edges'][terminalnode_label][2]]['ty']
		try:
			parent2_ty = parent2_ty['fun']['o']
			if ('fun' in parent2_ty or 'any' in parent2_ty) and ('S()' in str(parent_expression3['data']) or 'A()' in str(parent_expression3['data']) or 'GC()' in str(parent_expression3['data'])):
				monadic_in3 = 1
			else:
				monadic_in3 = 0
		except:
			parent2_ty = None
			monadic_in3 = 0
		######## If input 3 is a function type or any type Check if input 3 contains any monadic function  

			
		####### if all 3 inputs dont have any monadic functions then the recurse node is side effect free
		if	 monadic_in1 == 0 and monadic_in2 == 0 and monadic_in3 ==0 and node_output !=None:
		#if 'iW()' not in str(parent_expression1['data']) and 'iW()' not in str(parent_expression2['data']) and 'iW()' not in str(parent_expression3['data']): # all three inputs doesn't have any side effects
			current_expression = {'data':node_output,'world':best_world}
		else: # some inputs have effects
			current_data = Symbol('{{'+str(parent_expression1['data'])+'}X{'+str(parent_expression2['data'])+'}X{'+str(parent_expression3['data'])+'}}.zipping()')
			best_world +='.'+(str(current_data))
			current_expression = {'data':current_data,'world':best_world}
			

			
	elif node_name == 'getNnum':
		parent_expression1 = terminalnode.links[0].program_expression
		parent_expression2 = terminalnode.links[1].program_expression   
		if  len(parent_expression1['world']) > len(parent_expression2['world']):
			best_world = parent_expression1['world']
		else:
			best_world = parent_expression2['world']
		if is_number(parent_expression1['data']) and is_number(parent_expression2['data']) and node_output !=None:
			current_expression = {'data':node_output,'world':parent_expression1['world']}
		else:
			current_expression = {'data':Symbol('{{'+str(parent_expression1['data'])+'}X{'+str(parent_expression2['data'])+'}}.gNum()'),'world':best_world}			
	return current_expression
