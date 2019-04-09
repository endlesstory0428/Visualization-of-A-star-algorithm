#binary heap
class binaryH(object):
	def __init__(self):
		self.H = [] #heap
		self.Q = None #inherited queue
		return

	def __len__(self):
		return len(self.H)

	def __str__(self):
		return str(self.H)

	def __repr__(self):
		return repr(self.H)

	#connect with a queue
	def inheritQ(self, Q):
		#class priorityQ Q: inherited Q
		self.Q = Q
		for i in range(len(self.H)):
			self.Q.D[self.H[i][1]] = i
		return

	#build a heap using L
	def buildQ(self, L):
		#list L of (pri, val): inputing list

		#check format
		for item in L:
			if len(item) != 2:
				print('E: algorithm.binaryH.buildQ: not a (pri, val) tuple')
				exit()

		self.H = L
		if self.Q.D is not None:
			self.Q.D = dict()
			for i in range(len(self.H)):
				self.Q.D[self.H[i][1]] = i

		for i in reversed(range(len(L)//2)):
			self.siftdown(i)
		return
	
	#insert a new item
	def insert(self, item):
		#tuple item = (pri, val): new item

		#check format
		if len(item) != 2:
			print('E: algorithm.binaryH.insert: not a (pri, val) tuple')
			exit()

		self.H.append(item)
		if self.Q.D is not None:
			self.Q.D[item[1]] = len(self.H) - 1
		index = self.bubbleup(len(self.H) - 1)
		return

	#extract min
	def extract(self):
		item = self.H[0]
		if self.Q.D is not None:
			self.Q.D.pop(item[1])

		if len(self.H) > 1:
			temp = self.H.pop()
			self.H[0] = temp
			if self.Q.D is not None:
				self.Q.D[temp[1]] = 0
			self.siftdown(0)
		else: #len == 0
			item = self.H.pop()
		return item

	#erase the whole heap
	def clear(self):
		self.buildQ([])
		return


	def siftdown(self, pos):
		lPos = 2*pos + 1
		if lPos >= len(self.H):
			return

		rPos = lPos + 1
		if rPos < len(self.H) and self.H[lPos] > self.H[rPos]:
			sPos = lPos + 1
		else:
			sPos = lPos
		
		if self.H[pos] > self.H[sPos]:
			self.H[pos], self.H[sPos] = self.H[sPos], self.H[pos]
			if self.Q.D is not None:
				self.Q.D[self.H[pos][1]], self.Q.D[self.H[sPos][1]] = self.Q.D[self.H[sPos][1]], self.Q.D[self.H[pos][1]]
			self.siftdown(sPos)
		return


	def bubbleup(self, pos):
		if pos <= 0:
			return
		
		pPos = (pos - 1) // 2

		if self.H[pPos] > self.H[pos]:
			self.H[pPos], self.H[pos] = self.H[pos], self.H[pPos]
			if self.Q.D is not None:
				self.Q.D[self.H[pPos][1]], self.Q.D[self.H[pos][1]] = self.Q.D[self.H[pos][1]], self.Q.D[self.H[pPos][1]]
			self.bubbleup(pPos)
		return

#priority queue
class priorityQ(object):
	def __init__(self, H = None):
		#class binaryH H: based heap
		if H is None:
			H = binaryH()
		self.H = H 
		self.D = dict() #dict([val: index])

		self.H.inheritQ(self)
		return

	def __len__(self):
		return len(self.H)

	def __str__(self):
		return str(self.H)

	def __repr__(self):
		return repr(self.H)

	def buildQ(self, L):
		self.H.buildQ(L)
		return

	def insert(self, item):
		self.H.insert(item)
		return

	def extract(self):
		item = self.H.extract()
		return item

	def clear(self):
		self.H.clear()
		return

	#increase key
	def increase(self, val, pri):
		pos = self.D[val]
		self.H.H[pos] = (pri, val)
		self.H.siftdown(pos)
		return

	#decrease key
	def decrease(self, val, pri):
		pos = self.D[val]
		self.H.H[pos] = (pri, val)
		self.H.bubbleup(pos)
		return


#dijkstra's
class dijkstra(object):
	def __init__(self, vertexSet, edgeSet, vertexS, vertexG):
		self.vertexSet = vertexSet
		self.edgeSet = edgeSet
		self.vertexS = vertexS
		self.vertexG = vertexG
		self.QS = priorityQ() #priorityQ for S phase
		self.QG = priorityQ() #priorityQ for G phase
		return
		
	#common preprocess
	def preprocess(self):
		#clean mark
		for v in self.vertexSet.values():
			v.markS = False
			v.markG = False
		for e in self.edgeSet.values():
			e.mark = False

		#S phase
		for v in self.vertexSet.values():
			v.prevG = None
			v.distG = float('inf')
		self.vertexS.distG = 0
		LS = [(v.distG, v) for v in self.vertexSet.values()]
		self.QS.buildQ(LS)

		#G phase
		for v in self.vertexSet.values():
			v.prevS = None
			v.distS = float('inf')
		self.vertexG.distS = 0
		LG = [(v.distS, v) for v in self.vertexSet.values()]
		self.QG.buildQ(LG)
		return

	#use w as modified weight
	def preprocessDijkstra(self):
		for e in self.edgeSet.values():
			e.mWS = e.w
			e.mWG = e.w
		return

	#modify weight for BDA*
	def preprocessBDAS(self):
		for v in self.vertexSet.values():
			v.balancePotential()
		for e in self.edgeSet.values():
			e.modifyWeight()
		return

	#one iteration of loop
	def step(self, mark = False):
		if len(self.QS):
			pri, v = self.QS.extract()
			if pri == float('inf'):
				self.QS.clear()
			else:
				v.markS = mark
				for u, e in v.edgeSet.items():
					if u.distG > v.distG + e.mWS:
						u.distG = v.distG + e.mWS
						u.prevS = v
						self.QS.decrease(u, u.distG)
		
		if len(self.QG):
			pri, v = self.QG.extract()
			if pri == float('inf'):
				self.QG.clear()
			else:
				v.markG = mark
				for u, e in v.edgeRSet.items():
					if u.distS > v.distS + e.mWG:
						u.distS = v.distS + e.mWG
						u.prevG = v
						self.QG.decrease(u, u.distS)

		return

	#the whole loop for dijkstra's
	def dijkstraLoop(self):
		while self.QS or self.QG:
			self.step(mark = False)
		return

	#check step result for BDA*
	def BDASCheck(self):
		#returns:
		#True: loop should continue
		#False: there is intersection of S and G phase. stop
		#None: at least one phase is run out. the graph is not connected. stop.
		if self.QS and self.QG:
			if len(set(self.QS.D) | set(self.QG.D)) < len(self.vertexSet):
				return False
			else:
				return True
		else:
			return None

	#use the intersection vertex generate the whole path
	def generatePath(self, v):
		#class frame.vertex v: intersection vertex
		pS = []
		pG = []
		temp = v
		while temp is not None:
			pS.append(temp)
			temp = temp.prevS
		temp = v
		while temp is not None:
			pG.append(temp)
			temp = temp.prevG
		path = pS[: 0: -1] + pG
		return path

	#use the path to mark the edges
	def markPath(self, path):
		#list path with element frame.vertex: path from S to G
		posList = [v.pos for v in path]
		for i in range(len(posList) - 1):
			self.edgeSet[(posList[i], posList[i+1])].mark = True
		return

if __name__ == '__main__':
	h = binaryH()
	q = priorityQ(h)
	a = [(5,1),(5,2),(2,3),(4,4),(1,5)]
	q.buildQ(a)
	q.buildQ([])
	print(q)
	print(q.D)
	print(set(q.D))