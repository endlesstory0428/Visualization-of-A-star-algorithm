from queue import PriorityQueue

class vertex(object):
	def __init__(self, pos):
		#tuple pos of (int X, int Y): vertex pos
		self.pos = pos
		self.potentialS = 0 #estimated distance to Goal
		self.potentialG = 0 #estimated distance from Start
		self.bPotS = 0 #balanced potential S
		self.bPotG = 0 #balanced potential G
		self.edgeSet = dict() #edge from this vertex
		self.edgeRSet = dict() #edge to this vertex

		self.markS = False #S part visited, used to update paint
		self.markG = False #G part visited, used to update paint
		self.distS = float('inf') #dist to Goal
		self.distG = float('inf') #dist from Start
		self.prevS = None #prev vertex in S part
		self.prevG = None #prev vertex in G part
		self.warn = False
		return

	#used to debug
	def __str__(self):
		return 'frame.vertex: ' + str(self.pos) + ': ' + str(self.potentialS) + ', ' + str(self.potentialG)

	#DO NOT change, used in GUI to get index
	def __repr__(self):
		return str(self.pos)

	#cmp functions
	def __lt__(self, y):
		return self.pos < y.pos
	def __eq__(self, y):
		return self.pos == y.pos
	def __gt__(self, y):
		return self.pos > y.pos
	def __le__(self, y):
		return self.pos <= y.pos
	def __ge__(self, y):
		return self.pos >= y.pos
	def __ne__(self, y):
		return self.pos != y.pos

	#hash function
	def __hash__(self):
		return hash(self.pos)


	#tool functions
	#change potentials
	def setPotential(self, S, G):
		#int S in [0 : inf]:
		#int G in [0 : inf]:
		self.potentialS = S
		self.potentialG = G
		return

	#add out edge
	def addEdge(self, edge):
		#edge edge: out edge
		self.edgeSet[edge.v] = edge
		return

	#add in edge
	def addEdgeR(self, edge):
		#edge edge: in edge
		self.edgeRSet[edge.u] = edge
		return

	#get out edges
	def getEdge(self):
		return self.edgeSet.values()

	#get out neighbors
	def getNeighbor(self):
		return self.edgeSet.keys()

	#get in edges
	def getEdgeR(self):
		return self.edgeRSet.values()

	#get in neighbors
	def getNeighborR(self):
		return self.edgeRSet.keys()

	#delete an out edge
	def removeEdge(self, edge):
		#edge edge: deleted edge
		if edge.v in self.edgeSet:
			self.edgeSet.pop(edge.v)
		else:
			print('E: frame.vertex.removeEdge. Wrong edge.')
		return

	#delete an in edge
	def removeEdgeR(self, edge):
		#edge edge: deleted edge
		if edge.u in self.edgeRSet:
			self.edgeRSet.pop(edge.u)
		else:
			print('E: frame.vertex.removeEdgeR. Wrong edge.')
		return

	#check if potentials are admissive
	def checkPotential(self):
		#TODO: check distS >= potential S and distG >= potential G
		if self.distS < self.potentialS or self.distG < self.potentialG:
			self.warn = True
		return self.warn

	#balance potentialS and potentialG
	def balancePotential(self):
		self.bPotS = (self.potentialS - self.potentialG) / 2.
		self.bPotG = -self.bPotS
		return

	def encode(self):
		return (self.pos, self.potentialS, self.potentialG)


class edge(object):
	def __init__(self, u, v):
		#vertex u: out vertex
		#vertex v: in vertex
		self.u = u 
		self.v = v 
		self.w = 1 #weight
		self.mWS = 0 #modified weight for S part
		self.mWG = 0 #modified weight for G part
		self.mark = False
		return

	#used to debug
	def __str__(self):
		return 'frame.edge: ' + str(self.u.pos) + ', ' + str(self.v.pos) + ': ' + str(self.w)

	#DO NOT change, used in GUI to get index
	def __repr__(self):
		return str((self.u.pos, self.v.pos))

	#cmp functions
	def __lt__(self, y):
		return (self.u.pos, self.v.pos) < (y.u.pos, y.v.pos)
	def __eq__(self, y):
		return (self.u.pos, self.v.pos) == (y.u.pos, y.v.pos)
	def __gt__(self, y):
		return (self.u.pos, self.v.pos) > (y.u.pos, y.v.pos)
	def __le__(self, y):
		return (self.u.pos, self.v.pos) <= (y.u.pos, y.v.pos)
	def __ge__(self, y):
		return (self.u.pos, self.v.pos) >= (y.u.pos, y.v.pos)
	def __ne__(self, y):
		return (self.u.pos, self.v.pos) != (y.u.pos, y.v.pos)

	#hash function
	def __hash__(self):
		return hash((self.u.pos, self.v.pos))

	#change weight
	def setWeight(self, w):
		#int w in [0 : inf]: new weight
		self.w = w
		return

	#use balanced potential to modify weight
	def modifyWeight(self):
		self.mWS = self.w - (self.u.bPotS - self.v.bPotS)
		self.mWG = self.w - (self.v.bPotG - self.u.bPotG)
		return

	def encode(self):
		return (self.u.pos, self.v.pos, self.w)