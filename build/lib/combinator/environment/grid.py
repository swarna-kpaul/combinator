
####### Sample gridworld environment

##### environment should be an instance of a class

###### mandatory Methods
## reset : None --> None ######### should reset the environment
## get_observation : None --> Any return type ##### get the current observation 
## take_action : Any Input type --> None ######### take action based on input
## get_reward : None --> Number ######### return  normalized total reward between -1 and 1
## check_goalstate : None --> Boolean ########## check if goal is reached
## get_state : None --> dict ###### output current state
import pickle

class gridworld:
	def __init__(self,maze_def,init_state,goal_state, max_reward,min_reward):
		self.update_grid(maze_def,init_state,goal_state, max_reward,min_reward)
		
	def update_grid(self,maze_def,init_state,goal_state, max_reward,min_reward):
		self.maze_def = maze_def
		self.init_state = init_state
		self.goal_state = goal_state
		self.state = pickle.loads(pickle.dumps({'state':init_state, 'maze_def':maze_def},-1))
		self.curr_reward = 0
		self.total_reward = 0
		self.max_reward = max_reward
		self.min_reward = min_reward
		self.flag = 0
		self.temp_maze_def = pickle.loads(pickle.dumps(maze_def,-1))
		
		
	def reset (self):
		self.state['state'] = pickle.loads(pickle.dumps(self.init_state,-1))
		self.total_reward = 0
		self.curr_reward = 0
		self.temp_maze_def = pickle.loads(pickle.dumps(self.state['maze_def'],-1))
			
	def get_observation(self):
		if self.curr_reward <0 :
			return True
		else:
			return False
			
	def get_state(self):
		return self.state
		
	def set_state(self,state):
		self.state = state
	
	def take_action(self,action):
		current_state = pickle.loads(pickle.dumps(self.state['state'],-1))
		#maze_def = self.state['maze_def']
		########### Take action
		if action == 1:  ######### Front
			current_state[0] = current_state[0] + 1
		elif action == 2:  ####### Right
			current_state[1] = current_state[1] + 1
		elif action == 3:  ####### Left
			current_state[1] = current_state[1] - 1
		elif action == 4: ####### Back
			current_state[0] = current_state[0] - 1
		else:
			raise ValueError

		x = current_state[0] 
		y = current_state[1]
		if x >= len(self.temp_maze_def) or y >= len(self.temp_maze_def[0]):
			self.curr_reward = -0.01
		else:
			if self.temp_maze_def[x][y] == 1:
				self.curr_reward = -0.01
				self.state['state'] = current_state
			else:
				self.state['state'] = current_state
				self.curr_reward = self.temp_maze_def[x][y]
				if  self.curr_reward > 0:
					self.temp_maze_def[x][y] = 0  
		
		self.total_reward += self.curr_reward
		#if x == 12 and y == 1:
		#	self.flag =1
		#	print(self.total_reward)
		
		return 

	def get_reward(self):
		return self.total_reward/self.max_reward
		
	def check_goalstate(self,data):
		self.state['maze_def'] = pickle.loads(pickle.dumps(self.temp_maze_def,-1))
		if self.state['state'] == self.goal_state:#self.state['state'][0] >= self.goal_state[0] and self.state['state'][1] >= self.goal_state[1]:
			return True
		else:
			return False

init_state = [1,1]
goal_state = [20,20]


maze_def = [[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
			[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
			[1,0.99,0.99,1,0,1,1,1,1,1,0,0,1,0,0,0,0,0,0,1,0,1],
			[1,0,0,0,1,1,0,0,0,0,0,0,1,0,1,1,1,1,0,1,0,1],
			[1,0,1,0,0,1,0,1,0,1,1,1,1,0,1,0,0,0,0,1,0,1],
			[1,0,0,1,0,0,0,1,0,0,1,0,0,1,1,0,0,0,1,1,0,1],
			[1,0,0,1,1,0,0,1,0,0,1,0,0,0,0,0,0,0,0,0,0,1],
			[1,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,0,0,1,1,1],
			[1,0,1,0,1,0,1,0,0,1,1,0,0,0,0,0,0,0,0,1,0,1],
			[1,0,1,0,0,0,0,0,0,0,1,0,0,1,1,0,1,0,0,1,0,1],
			[1,0,1,0,1,1,1,1,0,0,.99,0,0,0,1,0,1,1,1,1,0,1],
			[1,0,1,0,0,0,0,1,1,1,0,0,1,1,0,0,0,0,0,1,0,1],
			[1,.99,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,1],
			[1,0,1,0,0,1,1,1,0,1,0,1,0,0,1,0,0,0,0,0,0,1],
			[1,0,1,1,0,0,0,1,0,1,0,0,0,0,0,1,1,1,0,1,0,1],
			[1,0,0,0,0,0,0,0,0,1,1,1,0,1,0,0,0,0,0,1,0,1],
			[1,0,0,1,1,1,1,1,0,1,0,0,0,0,1,0,0,1,1,1,0,1],
			[1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1],
			[1,0,1,1,1,1,1,0,0,0,0,1,1,1,1,1,0,0,0,1,0,1],
			[1,0,0,0,0,0,0,0,1,0,0,1,0,0,0,0,0,1,0,0,0,1],
			[1,0,0,0,0,0,0,0,1,0,0,1,0,0,0,0,0,1,0,0,.99,1],
			[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]]
    

grid_world = gridworld(maze_def,init_state,goal_state,5,-10)