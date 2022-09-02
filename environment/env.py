from environment.apienv import *
import time
import os
import psutil
import traceback

class world_exception(Exception):
	pass

class world_pending_exception(Exception):
	pass

class world:
	
	def __init__(self,env_func_obj,out_data_type='any'):
		self.update_env(env_func_obj,out_data_type)
		self.envtime_sec = 0
		self.PHASE = 2
		self.upper_PHASE = 2
		self.beam_PHASE = 2
		self.start_node_label_exec = 0
		self.end_node_label_exec = 0
		self.total_runtime = 0
		
	def reset(self):
		self.version = 0
		self.world_failed = 0
		self.runtime = 0
		self.obs = None
		self.world_funct.reset()
		
	def update_env(self,env_func_obj,out_data_type='any'):
		self.data_type = out_data_type
		self.version = 0
		self.world_funct = env_func_obj
		self.obs = None
		self.world_failed = 0
		self.runtime = 0
	
	def get_data(self,remoteserviceheader={}):
		self.obs = self.world_funct.get_observation(remoteserviceheader)
		return self.obs
		
	def upgrade(self):
		self.version +=1
	
	def put_action(self,action,remoteserviceheader={}):
		process = psutil.Process(os.getpid())
		tick = time.time()
		try:
		#if 1 ==1:
			self.world_funct.take_action(action,remoteserviceheader) #self.world_funct(self.maze_def,self.state,action)
			self.runtime += 1
			#self.total_runtime += 1
			tock = time.time()
			self.envtime_sec += tock - tick
		except Exception as e:
			traceback.print_exc()
			#print("action except",e)
			self.world_failed = 1
			tock = time.time()
			self.envtime_sec += tock - tick
			raise world_exception(str(e))
		if self.world_funct.pending_state == 1:
			self.world_funct.pending_state = 0	
			raise world_pending_exception('client comm pending')
		
	
	def funct(self):
		return {'world':self}
		
	def check_goal_state(self,data,remoteserviceheader={}):
		process = psutil.Process(os.getpid())
		try:
			tick = time.time()
			output = self.world_funct.check_goalstate(data,remoteserviceheader)
			tock = time.time()
			self.envtime_sec += tock - tick
		except Exception as e:
			#print("goal state except",e)
			self.world_failed = 1
			tock = time.time()
			self.envtime_sec += tock - tick
			raise world_exception(str(e))
		return output
			
	def get_reward(self,*data):
		return self.world_funct.get_reward()
		
	def get_state(self):
		return self.world_funct.get_state()
		
	def set_state(self,state):
		return self.world_funct.set_state(state)
    
######### initialize world
init_world = world(api_world)