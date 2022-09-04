# Combinator
### The programming model to integrate AI components 

[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://travis-ci.org/joemccann/dillinger)

Combinator is a programming model to build integrative AI solutions. Programs can be generated in the form of graphs such that functions are represented by nodes and dataflow between them by edges. It loosly follows the functional style of programming with lazy evaluation. The features of the programming model can be enumerated as following.

- Dynamical program generation - Can generate aribitrary subprograms at runtime
- Modularity - Every part of the program is modular 
- Expressivity - Preloaded with required primitives to build complex logics
- Abstraction - Can build arbitrary reusable components
- Ease of integration - With a proper UI programs can be easily built by connection nodes with edges. 
- API integration - This packaged model contains a basic version of the environment object to make post calls to remote APIs

For more details please check [this](https://link.springer.com/article/10.1007/s40031-021-00676-5) paper and [this](https://www.tandfonline.com/doi/abs/10.1080/03772063.2021.2004461) one.

### Get started
The programming model is built on Python. You can install the package by running the following command

```python
pip install combinator
```

Then load the package in Python by running the following command
```python
import combinator as cb
```

### Examples
Here are few program examples in combinator

##### Add two constant numbers
```Python
from combinator import creategraph, createnode, addlink, init_world, runp
operation = '+' # this example can be run by setting operation as '-' or '*' or '/' or '^' or '=' or '>'
graph = creategraph('TestGraph') # Takes graphname as argument
g1 = createnode(graph,'iW',init_world) # 1st argument should be the graph object, 2nd the node short name and 3rd argument should be specific parameters needed to create specific nodes. Except for initworld, constant, sensor and actuator 3rd argument is not needed. 
g2 = createnode(graph,'K',2);
g3 = createnode(graph,'K',3)
g4 = createnode(graph,operation)
addlink(graph,g1); 
addlink(graph,g2,g1); # first argument should be the graph object, 2nd the node which needs to be connect to its parents and rest of the arguments should be the parent nodes in sequence.
addlink(graph,g3,g1);
addlink(graph,g4,g3,g2);
output = runp(g4,graph) # The first argument should be the terminal node which needs to be run and 2nd the graph object
print (output[0])
```
##### Conjuction of two boolean values
```python
from combinator import creategraph, createnode, addlink, init_world, runp
operation = '&' # this example can also be run by setting operation as '|'
graph = creategraph()
g1 = createnode(graph,'iW',init_world)
g2 = createnode(graph,'K',True);
g3 = createnode(graph,'K',False)
g4 = createnode(graph,operation)
addlink(graph,g1);
addlink(graph,g2,g1);
addlink(graph,g3,g1);
addlink(graph,g4,g3,g2);
output = runp(g4,graph)
print (output[0])
```
##### Conditional execution
```python
from combinator import creategraph, createnode, addlink, init_world, runp
graph = creategraph()
g1 = createnode(graph,'iW',init_world)
g2 = createnode(graph,'K',2)
g3 = createnode(graph,'K',3);
g4 = createnode(graph,'=')
g5 = createnode(graph,'if')
addlink(graph,g1);addlink(graph,g2,g1);addlink(graph,g3,g1);addlink(graph,g4,g2,g3);addlink(graph,g5,g4,g1,g2);
output = runp(g5,graph)
print(output[0])
```

##### Square all elements of list with fmap
```python
from combinator import creategraph, createnode, addlink, init_world, runp
graph = creategraph()
g1 = createnode(graph,'iW',init_world)
g2 = createnode(graph,'K',[3,4,5]);
g3 = createnode(graph,'*')
g4 = createnode(graph,'fm')
addlink(graph,g1);addlink(graph,g2,g1);addlink(graph,g3,g1,g1);addlink(graph,g4,g3,g2);
output = runp(g4,graph)
print(output[0])
```

##### Zip two lists
```python
from combinator import creategraph, createnode, addlink, init_world, runp
graph = creategraph()
g1 = createnode(graph,'iW',init_world)
g2 = createnode(graph,'K',[3,4,5]);
g3 = createnode(graph,'K',[14,12,4]);
g4 = createnode(graph,'zp')
addlink(graph,g1);addlink(graph,g2,g1);addlink(graph,g3,g1);addlink(graph,g4,g3,g2);
output = runp(g4,graph)
print(output[0])
```

##### Run loop
```python
from combinator import creategraph, createnode, addlink, init_world, runp
graph = creategraph()
g1 = createnode(graph,'iW',init_world)
g2 = createnode(graph,'K',2);
g3 = createnode(graph,'+')
g4 = createnode(graph,'lp')
addlink(graph,g1);addlink(graph,g2,g1);addlink(graph,g3,g1,g1);addlink(graph,g4,g3,g2);
output = runp(g4,graph)
print(output[0])
```

##### Run Recurse
```python
from combinator import creategraph, createnode, addlink, init_world, runp
graph = creategraph()
g1 = createnode(graph,'iW',init_world)
g2 = createnode(graph,'K',7);
g3 = createnode(graph,'K',1);
g4 = createnode(graph,'+');
g5 = createnode(graph,'K',100);
g6 = createnode(graph,'>');
g7 = createnode(graph,'lg')
g8 = createnode(graph,'lg')
g9 = createnode(graph,'rc')
addlink(graph,g1);addlink(graph,g2,g1);addlink(graph,g3,g1);addlink(graph,g4,g3,g1);addlink(graph,g5,g1);addlink(graph,g6,g1,g5);addlink(graph,g7,g6);addlink(graph,g8,g4);addlink(graph,g9,g8,g7,g2);
output = runp(g4,graph)
print(output[0])
```

##### API POST call with actuator and sensor
```python
from combinator import creategraph, createnode, addlink, init_world, runp
graph = creategraph()
g1 = createnode(graph,'iW',init_world)
g2 = createnode(graph,'K',{'url':'https://httpbin.org/post','headers':{'Content-Type':'application/json'}})
g3 = createnode(graph,'K','');
g4 = createnode(graph,'ac','dict'); # the third argument in actuator or sensor node is the input type and output type respectively. If no argument is supplied the type is set as 'any'
g5 = createnode(graph,'sn','any');
g6 = createnode(graph,'ac','char');
g7 = createnode(graph,'sn','any');
addlink(graph,g1);addlink(graph,g2,g1);addlink(graph,g4,g2);
addlink(graph,g5,g4);addlink(graph,g3,g5);addlink(graph,g6,g3);addlink(graph,g7,g6);
output = runp(g4,graph)
print(output[0])
```

##### Update the environment 
```python
from combinator import init_world
init_world.update_env(<environment object>) # check environment/apienv.py to find out how to build an environment object. It can serve as an template to build your own custom environment object
```


### List of available primitives

Following are the list of available primitives in combinator:

-------------------------------------------------------------------------

| Full Name | short name | Description|
|-----------|------------|------------|
| initWorld | iW | Initializes the environment|
| constant  | K  | Outputs a constant value as set during node creation |
| identity  | id  | Outputs the input value unchanged |
| add  | +  | Adds two input numbers. Joins two lists. Updates 2nd key-value pair in the 1st. |
| subtract  | -  | Subtracts the number in 2nd input port from the 1st |
| multiply  | *  | Multiplies two numbers |
| divide  | /  | Divides the number in 1st input port with respect to the 2nd |
| exponent  | ^  | Raises the number in the 1st input port to the power of the 2nd |
| conjunction  | &  | Does logical AND operation between two inputs |
| disjunction  | \|  | Does logical OR operation between two inputs |
| negate  | !  | Inverts the input boolean value |
| greater  |>  | Outputs True if 1st input is greater than second else False |
| equal  |=  | Outputs True if 1st input is equal to second else False |
| emptylistordict  |nl  | Outputs empty key-value pair if input is 'keyvalue' else empty list |
| head  |hd  | Outputs 1st element of the list |
| tail  |tl | Outputs rest of the list except the 1st element |
| pop  |pop | Outputs the _n_ th element from the list in the 2nd input port. The value _n_ should be provided in the 1st input port. It fetches the value corresponding to the key _k_ if 1st input is a key-value pair. In that case the 2nd input should provide the key _k_.  |
|append| cn | Appends an element _e_ to the list provided in the 2nd input, where the 1st input provides the element _e_ |
|addkey| ak | Adds a key value pair to the key-value pairs provided in the 1st input. The 2nd input should provide the key and 3rd the value. |
|condition| if | Executes the parent graph connected to 2nd input port if 1st input is True else the parent graph of 3rd input port is executed. |
|lambdagraph| lg | Outputs the parent graph as subgraph. The iW node in the subgraph is replaced with an identity node. Any other initial nodes in the subgraph is connected to the newly created idenity node. |
|apply| ap | Outputs the parent graph as subgraph. The iW node in the subgraph is replaced with an identity node. Any other initial nodes in the subgraph is connected to the newly created idenity node. |
|fmap| fm | Converts the subgraph corresponding to parentnode1, a function and thereby applies it to each element of the list supplied in the input port 2. It outputs the new list. |
|zip| zp | Joins two list element wise. The two list should be provided in two input ports. It outputs a list of lists. |
|aggregator| ag | Aggregates the element of a list by an aggregator function. The aggregator function should be provided in input port 1 and the list in input port 2. |
|loop| lp | Converts the subgraph corresponding to parentnode1, a function and applies it _n_ number of times to its output. The initial argument of the function will be _n_ , where _n_ is supplied as an integer to its input port 2. |
|recurse| rc | Takes 2 function and one data value of any type as input. The function supplied to input port 1 is applied recursively on the 3rd input until stopping condition is met. The function supplied to input port 2 is applied on 3rd input to evaluate the stopping condition. |
|sensor| sn | sends a read request to the environment and outputs the recieved data|
|actuator| ac | sends and write request to the environment and writes the input data|