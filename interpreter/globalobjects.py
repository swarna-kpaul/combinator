from environment.env import *
import pickle

atype = {'iW':{'fun':{'i':['None'],'o':['any']}},
		'+':{'fun':{'i':['any','any'],'o':['any']}}, 
		'id':{'fun':{'i':['any'],'o':['any']}},
		'K':{'fun':{'i':['any'],'o':['any']}},
		'-':{'fun':{'i':['num','num'],'o':['num']}},
		'*':{'fun':{'i':['num','num'],'o':['num']}},
		'/':{'fun':{'i':['num','num'],'o':['num']}},
		'^':{'fun':{'i':['num','num'],'o':['num']}},
		'if':{'fun':{'i':['bool','any','any'],'o':['any']}},
		'=':{'fun':{'i':['any','any'],'o':['bool']}},
		'>':{'fun':{'i':['num','num'],'o':['bool']}}, 
		'&':{'fun':{'i':['bool','bool'],'o':['bool']}},
		'|':{'fun':{'i':['bool','bool'],'o':['bool']}},
		'!':{'fun':{'i':['bool'],'o':['bool']}},
		'hd':{'fun':{'i':['list'],'o':['any']}},
		'tl':{'fun':{'i':['list'],'o':['list']}},
		'cn': {'fun':{'i':['any','list'],'o':['list']}},
		'nl':{'fun':{'i':['any'],'o':['list']}},
		'ap': {'fun':{'i':['fun','any'],'o':['any']}},
		'fm':{'fun':{'i':['fun','list'],'o':['list']}}, 
		'zp':{'fun':{'i':['fun','list','list'],'o':['list']}}, 
		'ag':{'fun':{'i':['fun','list'],'o':['any']}},
		'rc':{'fun':{'i':['fun','fun','any'],'o':['any']}}, 
		'sn':{'fun':{'i':['world'],'o':['any']}},
		'ac':{'fun':{'i':['any'],'o':['world']}}, 
		'gc':{'fun':{'i':['any'],'o':['bool']}},
		'wm':{'fun':{'i':['any','any'],'o':['any']}},
		'lg':{'fun':{'i':['any'],'o':['fun']}},
		'lp':{'fun':{'i':['any','num'],'o':['any']}},
		'pop':{'fun':{'i':['any','any'],'o':['any']}},
		'pt':{'fun':{'i':['any'],'o':['any']}},
		'ak':{'fun':{'i':['dict','any','any'],'o':['dict']}}}

no_of_args = {'iW':0,'+':2,'id':1, 'K': 1,'-':2,'*':2,'/':2,'^':2,'if':3,'=':2,'>':2,'&':2,'|':2,'!':1,'hd':1,'tl':1,'cn':2,'nl':1,'ap':2,'fm':2,'zp':3,'ag':2,'rc':3,'sn':1,'ac':1,'gc':1,'wm':2,'lg':1,'gp':1, 'lp':2,'pop':2,'pt':1,'ak':3}



class globalobject:
	def __init__(self):
		self.corpus_of_all_objects = {0:{'nm':'iW','param':init_world, 'typ':{'fun':{'i':['None'],'o':['any']}}},
									1:{'nm':'K','param':1,'typ':{'fun':{'i':['any'],'o':['num']}}},
									2:{'nm':'id'},
									3:{'nm':'K','param':2, 'typ':{'fun':{'i':['any'],'o':['num']}}},
									4:{'nm':'/'},
									5:{'nm':'lg'},
									6:{'nm':'ap'},
									7:{'nm':'sn','param':'bool', 'typ':{'fun':{'i':['world'],'o':['bool']}}},
									8:{'nm':'ac','param':'num', 'typ':{'fun':{'i':['num'],'o':['world']}}},
									9:{'nm':'gc'},
									10:{'nm':'rc'},
									11:{'nm':'+'},
									12:{'nm':'-'},
									13:{'nm':'*'},
									14:{'nm':'if'},
									15:{'nm':'='},
									16:{'nm':'K','param':10000, 'typ':{'fun':{'i':['any'],'o':['num']}}},
									17:{'nm':'K','param':0, 'typ':{'fun':{'i':['any'],'o':['num']}}},
									18:{'nm':'K','param':3, 'typ':{'fun':{'i':['any'],'o':['num']}}},
									19:{'nm':'hd'},
									20:{'nm':'tl'},
									21:{'nm':'cn'},
									22:{'nm':'nl'},
									23:{'nm':'^'},
									24:{'nm':'ac','param':'list', 'typ':{'fun':{'i':['list'],'o':['world']}}},
									25:{'nm':'wm'},
									26:{'nm':'K','param':4, 'typ':{'fun':{'i':['any'],'o':['num']}}},
									27:{'nm':'K','param':8, 'typ':{'fun':{'i':['any'],'o':['num']}}},
									28:{'nm':'K','param':16, 'typ':{'fun':{'i':['any'],'o':['num']}}},
									29:{'nm':'K','param':32, 'typ':{'fun':{'i':['any'],'o':['num']}}},
									32:{'nm':'K','param':64, 'typ':{'fun':{'i':['any'],'o':['num']}}},
									30:{'nm':'lp'},
									31:{'nm':'sn','param':'num', 'typ':{'fun':{'i':['world'],'o':['num']}}},
									32:{'nm':'K','param':5, 'typ':{'fun':{'i':['any'],'o':['num']}}},}
		self.corpus_index= [0,1,2,3,4,5,6,7,8,10,11,15,16] #[0,1,3,5,7,8,10,17,18]
		self.type_compatible_node_links = {}
		self.total_runtime = 0 
		self.total_beamruntime = 0 
		self.tottime_sec = 0
		self.searchertime_sec = 0
		self.envtime_sec=0
		self.starttime = 0
		self.beamwidth =20
		
	def resettime(self):
		self.total_runtime = 0
		self.total_beamruntime = 0 
		
	def update_corpus(self,id,arg): ## id -> index , arg --> node definition
		self.corpus_of_all_objects[id] = arg
	
	def update_corpus_index(self, id):
		self.corpus_index.append(id)
		
	def reset_corpus_index(self, CI):
		self.corpus_index = CI
	
	def update_pint(self, type_compatible_node_links):
		self.type_compatible_node_links = pickle.loads(pickle.dumps(type_compatible_node_links,-1))
#corpus_index=[0,1,2,3,4,5,6,7,8,10,11,15,16]

corpusInstance = globalobject()
#corpusInstance.reset_corpus_index([0,1,3,5,7,8,10,17,18])

C = 0.01
alpha = 0.5
PHASErunlimit = 0
L = 0.8