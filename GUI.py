import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import time

import frame
import algorithm as alg
import plugin

class window(QWidget):
	#main window
	def __init__(self, parent = None):
		super(window, self).__init__(parent)
		self.setWindowTitle("Visualization of BDA*")
		#layout
		self.layoutWindow()
		#slot
		self.connectSlot()
		return

	#layout functions
	#main window
	def layoutWindow(self):
		layout = QGridLayout(self)

		menu = self.layoutMenu()
		area = self.layoutArea()

		layout.addWidget(menu, 0, 1)
		layout.addWidget(area, 0, 0)

		self.setLayout(layout)
		return

	#menu and tools
	def layoutMenu(self):
		menu = QSplitter(Qt.Vertical)
		menu.setOpaqueResize(True)

		#tools
		self.toolComboBox = QComboBox()
		self.toolComboBox.addItem('vertex', 'VN')
		self.toolComboBox.addItem('edge', 'EN')
		self.toolComboBox.addItem('vertex S', 'VS')
		self.toolComboBox.addItem('vertex G', 'VG')
		self.toolComboBox.addItem('edit vertex', 'VE')
		self.toolComboBox.addItem('edit edge', 'EE')
		self.toolComboBox.addItem('delete vertex', 'VD')
		self.toolComboBox.addItem('delete edge', 'ED')

		#menu buttons
		self.clearBtn = QPushButton('Clear', menu)
		self.randomBtn = QPushButton('Random Graph', menu)
		self.confirmBtn = QPushButton('Confirm', menu)
		self.BDASBtn = QPushButton('BDA*', menu)
		self.BDASBtn.setEnabled(False)
		self.saveBtn = QPushButton('Save', menu)
		self.loadBtn = QPushButton('Load', menu)

		frame = QFrame(menu)
		layout = QGridLayout(frame)
		layout.setSpacing(8)

		layout.addWidget(self.toolComboBox)
		layout.addWidget(self.clearBtn)
		layout.addWidget(self.randomBtn)
		layout.addWidget(self.confirmBtn)
		layout.addWidget(self.BDASBtn)
		layout.addWidget(self.saveBtn)
		layout.addWidget(self.loadBtn)

		return menu

	#paint area
	def layoutArea(self):
		area = QSplitter(Qt.Horizontal)
		area.setOpaqueResize(True)

		stacked = QStackedWidget()
		stacked.setFrameStyle(QFrame.Panel | QFrame.Raised)
		
		self.area = paint(self)
		stacked.addWidget(self.area)

		frame = QFrame(area)
		layout = QVBoxLayout(frame)
		layout.setSpacing(8)

		layout.addWidget(stacked)

		return area

	#slot functions
	#signal.connect.functions
	def connectSlot(self):
		self.toolComboBox.activated.connect(self.slotTool)
		self.slotTool(self.toolComboBox.currentIndex())

		self.confirmBtn.clicked.connect(self.slotConfirm)
		self.BDASBtn.clicked.connect(self.slotBDAS)
		self.clearBtn.clicked.connect(self.slotClear)
		self.saveBtn.clicked.connect(self.slotSave)
		self.loadBtn.clicked.connect(self.slotLoad)
		self.randomBtn.clicked.connect(self.slotRandom)
		#TODO: other slots
		return

	#choose a tool
	def slotTool(self, value):
		#int value: index of the selected tool
		self.area.clearTemp()
		self.area.tool = value
		self.area.getTool()
		return

	def slotClear(self):
		self.area.clearTemp()
		res = QMessageBox.question(self, 'Clear', 'Are you sure to clear the graph?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
		if res == QMessageBox.Yes:
			self.area.vertexSet = dict()
			self.area.edgeSet = dict()
			self.area.vertexS = None
			self.area.vertexG = None
			

			self.area.update()
			self.BDASBtn.setEnabled(False)
		return

	def slotSave(self):
		self.area.clearTemp()
		graph = (self.area.vertexSet, self.area.edgeSet, self.area.vertexS, self.area.vertexG)
		plugin.saveG(graph, './', 'graph.pkl')
		QMessageBox.information(self, 'Save', 'The graph have been saved.')
		return

	def slotLoad(self):
		self.area.clearTemp()
		res = QMessageBox.question(self, 'Load', 'Are you sure to load the graph?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
		if res == QMessageBox.Yes:
			try:
				self.area.vertexSet, self.area.edgeSet, self.area.vertexS, self.area.vertexG = plugin.loadG('./', 'graph.pkl')
				self.area.update()
				self.BDASBtn.setEnabled(False)
			except BaseException:
				QMessageBox.critical(self, 'Load', 'Failed to load the graph.')
		return

	def slotRandom(self):
		self.area.clearTemp()
		res = QMessageBox.question(self, 'Random Graph', 'Are you sure to use a random graph?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
		if res == QMessageBox.Yes:
			self.area.vertexSet, self.area.edgeSet, self.area.vertexS, self.area.vertexG = plugin.randomG()
			self.area.update()
			self.BDASBtn.setEnabled(False)
		return


	#freeze vertexSet and edgeSet, check if the graph is legal.
	def slotConfirm(self):
		self.area.clearTemp()
		#check S and G existence
		if self.area.vertexS is None:
			QMessageBox.critical(self, 'No Start Vertex', 'Algorithm requires a start vertex.')
			return
		if self.area.vertexG is None:
			QMessageBox.critical(self, 'No Goal Vertex', 'Algorithm requires a goal vertex.')
			return
		
		#run dijkstra
		self.graph = alg.dijkstra(self.area.vertexSet, self.area.edgeSet, self.area.vertexS, self.area.vertexG)
		self.graph.preprocess()
		self.graph.preprocessDijkstra()
		self.graph.dijkstraLoop()
		
		warn = False
		#check connectivity
		if self.area.vertexG.distG == float('inf'):
			warn = True
			QMessageBox.warning(self, 'No Path', 'No path from S to G. \nTips: this is a direct graph.')
		
		res = False
		#check under-estimation
		for v in self.area.vertexSet.values():
			res = res or v.checkPotential()
		if res:
			warn = True
			QMessageBox.warning(self, 'Bad Estimation', 'Some estimations are over-estimated.')

		if not warn:
			QMessageBox.information(self, 'Check Complete', 'Now you can run BDA*.')
		self.BDASBtn.setEnabled(True)
		return


	#run BDA* step by step
	def slotBDAS(self):
		self.area.clearTemp()
		#preprocess
		self.graph.preprocess()
		self.graph.preprocessBDAS()
		#loop
		while True:
			self.graph.step(mark = True)
			self.area.update()

			#check step result
			res = self.graph.BDASCheck()
			if res is None: #not connected
				break
			elif res is False: #done
				path = []
				for v in self.area.vertexSet.values():
					if v.markS and v.markG:
						path = self.graph.generatePath(v)
						break
				self.graph.markPath(path)
				break

			QMessageBox.information(self, 'BDA*', 'one step.')
		QMessageBox.information(self, 'BDA*', 'Done!')
		return

class paint(QWidget):
	#paint area
	def __init__(self, main):
		#QWidget main: main window
		super(paint,self).__init__()
		self.main = main
		self.setPalette(QPalette(Qt.white))
		self.setAutoFillBackground(True)
		self.setMinimumSize(512, 512)
		self.pen = QPen()
		self.tool = 0

		self.vertex = False
		self.edge = False
		self.valid = False

		self.vertexPosX = -5
		self.vertexPosY = -5
		self.vertexPPosX = -5
		self.vertexPPosY = -5
		self.edgeSPosX = -5
		self.edgeSPosY = -5
		self.edgeGPosX = -5
		self.edgeGPosY = -5

		self.vertexSet = dict()
		self.edgeSet = dict()
		self.vertexS = None
		self.vertexG = None

		self.vertexSize = 7
		self.edgeSize = 3

		return
	
	def paintEvent(self, event):
		painter = QPainter()
		painter.begin(self)

		self.paintHistory(painter)

		self.getTool()
		painter.setPen(self.pen)

		if self.vertex:
			painter.drawPoint(QPoint(self.vertexPosX, self.vertexPosY))

		elif self.edge:
			painter.drawLine(self.edgeSPosX, self.edgeSPosY, self.edgeGPosX, self.edgeGPosY)

		painter.end()
		return

	#draw every known vertices and edges
	def paintHistory(self, painter):
		for pos, vertex in self.vertexSet.items():
			vertexSize = self.vertexSize
			if vertex.warn:
				vertexSize = vertexSize + 2
				vertex.warn = False

			if vertex is self.vertexS:
				pen = QPen(Qt.cyan, vertexSize, Qt.SolidLine)
			elif vertex is self.vertexG:
				pen = QPen(Qt.magenta, vertexSize, Qt.SolidLine)
			elif vertex.markS:
				vertexSize = vertexSize + 4
				pen = QPen(Qt.darkCyan, vertexSize, Qt.SolidLine)
			elif vertex.markG:
				vertexSize = vertexSize + 4
				pen = QPen(Qt.darkMagenta, vertexSize, Qt.SolidLine)
			else:
				pen = QPen(Qt.black, vertexSize, Qt.SolidLine)
			painter.setPen(pen)
			painter.drawPoint(QPoint(*pos))

		for pos, edge in self.edgeSet.items():
			edgeSize = self.edgeSize
			if edge.mark:
				edgeSize = edgeSize + 1
				pen = QPen(Qt.black, edgeSize, Qt.SolidLine)
				aPen = QPen(Qt.black, 2, Qt.SolidLine)
			else:
				pen = QPen(Qt.gray, edgeSize, Qt.SolidLine)
				aPen = QPen(Qt.gray, 2, Qt.SolidLine)
			
			u, v = pos
			painter.setPen(pen)
			painter.drawLine(*u, *v)

			a1, a2 = plugin.arrow(u, v, 15)
			painter.setPen(aPen)
			painter.drawLine(*a1, *v)
			painter.drawLine(*a2, *v)
		return

	def clearTemp(self):
		self.vertexPosX = -5
		self.vertexPosY = -5
		self.vertexPPosX = -5
		self.vertexPPosY = -5
		self.edgeSPosX = -5
		self.edgeSPosY = -5
		self.edgeGPosX = -5
		self.edgeGPosY = -5
		return

	def mousePressEvent(self, event):
		#new elements
		if self.tool == 0 or self.tool == 1 or self.tool == 2 or self.tool == 3:
			if self.vertex:
				self.vertexPosX, self.vertexPosY = self.getPos(event)
				self.valid = True

			elif self.edge:
				self.edgeSPosX, self.edgeSPosY = self.getPos(event)
				tUPos = (self.edgeSPosX, self.edgeSPosY)
				tUPos = self.matchVertex(tUPos)

				if tUPos[0] is not None:
					self.edgeSPosX, self.edgeSPosY = tUPos
					self.valid = True
				else:
					self.valid = False

		#edit elements
		elif self.tool == 4 or self.tool == 5:
			if self.vertex:
				self.vertexPosX, self.vertexPosY = self.getPos(event)
				tPos = (self.vertexPosX, self.vertexPosY)
				tPos = self.matchVertex(tPos)
				if tPos[0] is not None:
					self.vertexPPosX, self.vertexPPosY = tPos
					self.valid = True
				else:
					self.vertexPPosX, self.vertexPPosY = tPos
					self.valid = False

			elif self.edge:
				self.edgeSPosX, self.edgeSPosY = self.getPos(event)
				tUPos = (self.edgeSPosX, self.edgeSPosY)
				tUPos = self.matchVertex(tUPos)
				if tUPos[0] is not None:
					self.edgeSPosX, self.edgeSPosY = tUPos
					self.valid = True
				else:
					self.valid = False

		#delete elements
		elif self.tool == 6 or self.tool == 7:
			if self.vertex:
				self.vertexPosX, self.vertexPosY = self.getPos(event)
				tPos = (self.vertexPosX, self.vertexPosY)
				tPos = self.matchVertex(tPos)
				if tPos[0] is not None:
					self.vertexPPosX, self.vertexPPosY = tPos
					self.valid = True
				else:
					self.vertexPPosX, self.vertexPPosY = tPos
					self.valid = False

			elif self.edge:
				self.edgeSPosX, self.edgeSPosY = self.getPos(event)
				tUPos = (self.edgeSPosX, self.edgeSPosY)
				tUPos = self.matchVertex(tUPos)
				if tUPos[0] is not None:
					self.edgeSPosX, self.edgeSPosY = tUPos
					self.valid = True
				else:
					self.valid = False

		if self.vertex:
			self.update()
		return

	def mouseMoveEvent(self, event):
		if self.vertex:
			self.vertexPosX, self.vertexPosY = self.getPos(event)
		elif self.edge:
			self.edgeGPosX, self.edgeGPosY = self.getPos(event)
		self.update()
		return

	def mouseReleaseEvent(self, event):
		#new elements
		if self.tool == 0 or self.tool == 1 or self.tool == 2 or self.tool == 3:
			if self.vertex:
				self.vertexPosX, self.vertexPosY = self.getPos(event)
				tPos = (self.vertexPosX, self.vertexPosY)
				pos = self.matchVertex(tPos) #DO NOT use tPos instead of pos
				if pos[0] is not None:
					self.valid = False
				else:
					tempVertex = frame.vertex(tPos)
					res = self.editVertex(tempVertex)
					if not res:
						self.valid = False
					else:
						self.valid = True
						self.main.BDASBtn.setEnabled(False)
						self.vertexSet[tPos] = tempVertex
						if self.tool == 2:
							self.vertexS = tempVertex
						elif self.tool == 3:
							self.vertexG = tempVertex

			elif self.edge:
				self.edgeGPosX, self.edgeGPosY = self.getPos(event)
				tUPos = (self.edgeSPosX, self.edgeSPosY)
				tVPos = (self.edgeGPosX, self.edgeGPosY)
				if self.valid:
					tVPos = self.matchVertex(tVPos)
					if tVPos[0] is not None:
						if tUPos != tVPos:
							tPos = (tUPos, tVPos)
							self.edgeGPosX, self.edgeGPosY = tVPos
							tempEdge = frame.edge(self.vertexSet[tUPos], self.vertexSet[tVPos])
							res = self.editEdge(tempEdge)
							if not res:
								self.valid = False
							else:
								self.valid = True
								self.main.BDASBtn.setEnabled(False)
								self.edgeSet[tPos] = tempEdge
								self.vertexSet[tUPos].addEdge(tempEdge)
								self.vertexSet[tVPos].addEdgeR(tempEdge)
						else:
							self.valid = False
					else:
						self.valid = False

		#edit elementes
		elif self.tool == 4 or self.tool == 5:
			if self.vertex:
				self.vertexPosX, self.vertexPosY = self.getPos(event)
				tPos = (self.vertexPosX, self.vertexPosY)
				tPos = self.matchVertex(tPos)
				if tPos[0] is not None:
					if tPos != (self.vertexPPosX, self.vertexPPosY):
						self.valid = False
					else:
						self.vertexPosX, self.vertexPosY = tPos
						res = self.editVertex(self.vertexSet[tPos])
						if not res:
							self.valid = False
						else:
							self.valid = True
							self.main.BDASBtn.setEnabled(False)
				else:
					self.valid = False

			elif self.edge:
				self.edgeGPosX, self.edgeGPosY = self.getPos(event)
				tUPos = (self.edgeSPosX, self.edgeSPosY)
				tVPos = (self.edgeGPosX, self.edgeGPosY)
				if self.valid:
					tVPos = self.matchVertex(tVPos)
					if tVPos[0] is not None:
						tPos = (tUPos, tVPos)
						if tPos in self.edgeSet:
							self.edgeGPosX, self.edgeGPosY = tVPos
							res = self.editEdge(self.edgeSet[(tUPos, tVPos)])
							if not res:
								self.valid = False
							else:
								self.valid = True
								self.main.BDASBtn.setEnabled(False)
						else:
							self.valid = False
					else:
						self.valid = False

		#delete elements
		elif self.tool == 6 or self.tool == 7:
			if self.vertex:
				self.vertexPosX, self.vertexPosY = self.getPos(event)
				tPos = (self.vertexPosX, self.vertexPosY)
				tPos = self.matchVertex(tPos)
				if tPos[0] is not None:
					if tPos != (self.vertexPPosX, self.vertexPPosY):
						self.valid = False
					else:
						self.valid = True
						self.main.BDASBtn.setEnabled(False)
						self.vertexPosX, self.vertexPosY = tPos
						tempVertex = self.vertexSet.pop(tPos)
						self.deleteVertex(tempVertex)

						if tempVertex is self.vertexS:
							self.vertexS = None
						elif tempVertex is self.vertexG:
							self.vertexG = None
				else:
					self.valid = False

			elif self.edge:
				self.edgeGPosX, self.edgeGPosY = self.getPos(event)
				tUPos = (self.edgeSPosX, self.edgeSPosY)
				tVPos = (self.edgeGPosX, self.edgeGPosY)
				if self.valid:
					tVPos = self.matchVertex(tVPos)
					if tVPos[0] is not None:
						tPos = (tUPos, tVPos)
						if tPos in self.edgeSet:
							self.valid = True
							self.main.BDASBtn.setEnabled(False)
							self.edgeGPosX, self.edgeGPosY = tVPos
							tempEdge = self.edgeSet.pop(tPos)
							self.deleteEdge(tempEdge)
						else:
							self.valid = False
					else:
						self.valid = False

		self.update()
		return

	#update pen in order to draw temp elements
	def getTool(self):
		if self.tool == 0 or self.tool == 2 or self.tool == 3 or self.tool == 4 or self.tool == 6:
			self.vertex = True
			self.edge = False
			if self.valid:
				if self.tool == 2:
					self.pen = QPen(Qt.cyan, self.vertexSize, Qt.SolidLine)
				elif self.tool == 3:
					self.pen = QPen(Qt.magenta, self.vertexSize, Qt.SolidLine)
				elif self.tool == 4:
					self.pen = QPen(Qt.green, self.vertexSize, Qt.SolidLine)
				elif self.tool == 6:
					self.pen = QPen(Qt.yellow, self.vertexSize, Qt.SolidLine)
				else:
					self.pen = QPen(Qt.black, self.vertexSize, Qt.SolidLine)
			else:
				self.pen = QPen(Qt.red, self.vertexSize, Qt.SolidLine)

		elif self.tool == 1 or self.tool == 5 or self.tool == 7:
			self.vertex = False
			self.edge = True
			if self.valid:
				if self.tool == 5:
					self.pen = QPen(Qt.green, self.edgeSize, Qt.SolidLine)
				elif self.tool == 7:
					self.pen = QPen(Qt.yellow, self.edgeSize, Qt.SolidLine)
				else:
					self.pen = QPen(Qt.gray, self.edgeSize, Qt.SolidLine)
			else:
				self.pen = QPen(Qt.red, self.edgeSize, Qt.SolidLine)
		return

	#get mouse pos
	def getPos(self, event):
		return (event.pos().x(), event.pos().y())

	#check if there is a vertex at tempPos
	def matchVertex(self, tempPos):
		#tuple tempPos of (int X, int Y): temp mouse pos
		#return:
		#tuple vertexPos of (int X, int Y): vertex pos. If no vertices, (None, None)
		for pos, vertex in self.vertexSet.items():
			if pos[0] - self.vertexSize < tempPos[0] < pos[0] + self.vertexSize and pos[1] - self.vertexSize < tempPos[1] < pos[1] + self.vertexSize:
				return pos
		return (None, None)

	#delete (a vertex, )its related edges and update neighbors' edgeSet
	def deleteVertex(self, vertex):
		#frame.vertex vertex: deleted vertex
		for tempEdge in vertex.getEdge():
			self.edgeSet.pop(eval(repr(tempEdge)))
			tempEdge.v.removeEdgeR(tempEdge)
		for tempEdgeR in vertex.getEdgeR():
			self.edgeSet.pop(eval(repr(tempEdgeR)))
			tempEdgeR.u.removeEdge(tempEdgeR)
		return

	#delete (a edge )and update neighbors' edgeSet
	def deleteEdge(self, edge):
		#frame.edge edge: deleted edge
		self.vertexSet[eval(repr(edge.u))].removeEdge(edge)
		self.vertexSet[eval(repr(edge.v))].removeEdgeR(edge)
		return

	#change potentials of a vertex
	def editVertex(self, vertex):
		#frame.vertex vertex: edited vertex
		#return:
		#bool okay: True: valid edit; False: user cancel this edit
		potentialS, okay = QInputDialog.getInt(self, 'Step 1 / 2', 'Estimated distance to vertex G:', vertex.potentialS, 0, self.height()+self.width())
		if not okay:
			return False
		potentialG, okay = QInputDialog.getInt(self, 'Step 2 / 2', 'Estimated distance from vertex S:', vertex.potentialG, 0, self.height()+self.width())
		if not okay:
			return False
		vertex.setPotential(potentialS, potentialG)
		return True

	#change weight of a edge
	def editEdge(self, edge):
		#frame.edge edge: edited edge
		#return:
		#bool okay: True: valid edit; False: user cancel this edit
		weight, okay = QInputDialog.getInt(self, 'Step 1 / 1', 'Distance:', edge.w, 0, self.height()+self.width())
		if not okay:
			return False
		edge.setWeight(weight)
		return True


if __name__=='__main__':
	app = QApplication(sys.argv)
	form = window()
	form.show()
	app.exec_()