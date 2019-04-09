import pickle as pkl
import random
import math

import frame

# S&L part
def saveG(G, path, name):
	#tuple G of (vertexSet, edgeSet): graph. acturally, anything is ok
	#str path: saved file path. REMEMBER: end with a slash
	#str name: saved file name
	saveFile = open(path+name, 'wb')
	pkl.dump(encodeG(*G), saveFile)
	saveFile.close()
	return

def loadG(path, name):
	#str path: saved file path. REMEMBER: end with a slash
	#str name: saved file name
	#return:
	#tuple G of (vertexSet, edgeSet): graph. acturally, anything is ok
	loadFile = open(path+name, 'rb')
	G = pkl.load(loadFile)
	loadFile.close()
	return decodeG(*G)

def encodeG(V, E, S, G):
	VList = [v.encode() for v in V.values()]
	EList = [e.encode() for e in E.values()]
	if S is None:
		sPos = None
	else:
		sPos = S.pos
	if G is None:
		gPos = None
	else:
		gPos = G.pos
	return (tuple(VList), tuple(EList), sPos, gPos)

def decodeG(V, E, S, G):
	VSet = dict()
	for pos, pS, pG in V:
		v = frame.vertex(pos)
		v.setPotential(pS, pG)
		VSet[pos] = v

	ESet = dict()
	for uPos, vPos, w in E:
		u = VSet[uPos]
		v = VSet[vPos]
		e = frame.edge(u, v)
		e.setWeight(w)
		u.addEdge(e)
		v.addEdgeR(e)
		ESet[(uPos, vPos)] = e

	if S is None:
		vertexS = None
	else:
		vertexS = VSet[S]
	if G is None:
		vertexG = None
	else:
		vertexG = VSet[G]
	return (VSet, ESet, vertexS, vertexG)


#arrow part
def arrow(u, v, length):
	direction = (u[0] - v[0], u[1] - v[1])
	a1x, a1y = iTimes(direction, (2, 1))
	a2x, a2y = iTimes(direction, (2, -1))
	na1x, na1y = normalize(a1x, a1y, length)
	na2x, na2y = normalize(a2x, a2y, length)
	a1 = (v[0] + na1x, v[1] + na1y)
	a2 = (v[0] + na2x, v[1] + na2y)
	return (a1, a2)

def iTimes(x, y):
	a, b = x
	c, d = y
	#a+bi * c+di
	return (a*c - b*d, a*d + b*c)

def normalize(x, y, length):
	rate = length / pow(pow(x, 2) + pow(y, 2), 0.5)
	return (int(x * rate), int(y * rate))


#random graph part
def randomG():
	rows = random.randint(4, 16)
	cols = random.randint(4, 16)
	rowSize = 480 // rows
	colSize = 480 // cols
	safeMaxRowPos = rowSize - 8
	safeMaxColPos = rowSize - 8

	vertexList = []
	for row in range(rows):
		vertexList.append([])
		for col in range(cols):
			x = row * rowSize + random.randint(8, safeMaxRowPos)
			y = col * colSize + random.randint(8, safeMaxColPos)
			vertexList[row].append((x, y))
	
	vS = vertexList[0][0]
	vG = vertexList[rows-1][cols-1]

	VSet = dict()
	for row in range(rows):
		for col in range(cols):
			pos = vertexList[row][col]
			v = frame.vertex(pos)
			v.setPotential(getDist(pos, vG), getDist(pos, vS))
			VSet[pos] = v

	ESet = dict()
	for row in range(rows):
		for col in range(cols):
			uPos = vertexList[row][col]
			u = VSet[uPos]
			if row != rows - 1:
				vPos = vertexList[row+1][col]
				v = VSet[vPos]
				e = frame.edge(u, v)
				e.setWeight(getDist(uPos, vPos))
				u.addEdge(e)
				v.addEdgeR(e)
				ESet[(uPos, vPos)] = e
			if col != cols - 1:
				vPos = vertexList[row][col+1]
				v = VSet[vPos]
				e = frame.edge(u, v)
				e.setWeight(getDist(uPos, vPos))
				u.addEdge(e)
				v.addEdgeR(e)
				ESet[(uPos, vPos)] = e

	vertexS = VSet[vS]
	vertexG = VSet[vG]

	return (VSet, ESet, vertexS, vertexG)



def getDist(u, v):
	a, b = u
	c, d = v
	return math.floor(pow(pow(a-c, 2) + pow(b-d, 2), 0.5))

if __name__ == '__main__':
	vertexSet = dict()
	edgeSet = dict()
	a = frame.vertex((1,1))
	b = frame.vertex((2.2))
	vertexSet[(1,1)] = a
	vertexSet[(2,2)] = b
	e = frame.edge(a,b)
	edgeSet[((1,1), (2,2))] = e
	saveG((vertexSet, edgeSet), './', 'graph.pkl')