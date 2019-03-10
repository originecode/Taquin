#!/usr/local/bin/python3
# -*-coding:utf-8 -*
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton,QLabel,QComboBox,QCheckBox,QMessageBox
from PyQt5.QtGui import QFontDatabase,QFont
from PyQt5.QtCore import QSize,Qt
from random import shuffle
from math import sqrt,ceil
from collections import OrderedDict
import time

class Taquin:
	def __init__(self, environment, previous=None, move=None):
		self.environment = environment
		self.previous = previous
		self.inv = None
		self.dis = None
		self.man = None
		self.h = None
		if previous == None:
			self.path = "_"
			self.g = 0
			self.sequence = self.magic(1)
		else:
			self.path = previous.path + move
			self.g = previous.g + 1
			self.sequence = previous.sequence.copy()
			self.moveTile(move)
			self.inv,self.dis,self.man,self.h = self.details()
		self.moves = self.findMoves()
		self.f = self.h + self.g
	def coordinates(self, content=0):
		width = self.environment.sizes[0]
		if isinstance(content, list):
			return (width * content[1]) + content[0]
		else:
			index = self.sequence.index(content)
			y = ceil((index + 1) / width) - 1
			x = index - (y * width)
			return [x, y]

	def details(self):
		width, length = self.environment.sizes
		weightings = self.environment.weightings
		sequence = self.sequence
		inv = 0
		dis = 0
		man = 0
		h = 0
		for weighting in weightings:
			k = 0
			stepH = 0
			for i in range(0,length):
				stepMan = 0
				if weighting == weightings[0]:
					for j in range(i+1,length):
						if sequence[i] != 0 and sequence[j] != 0 and sequence[i] > sequence[j]: inv += 1
					if sequence[i] != 0 and sequence[i] != (i+1):
						dis += 1
				if i > 0:
					pos = self.coordinates(i)
					x = i % width
					coords = (((width - 1) if x == 0 else (x - 1)), ceil(i / width) - 1)
					stepMan += (abs(pos[0] - coords[0]) + abs(pos[1] - coords[1]))
					if weighting == weightings[0]: man += stepMan
					stepH += weighting[0][k] * stepMan
					k += 1
			if weighting[1] > 1: stepH /= weighting[1]
			if weighting[2] == 7: h += dis
			else: h += stepH
		return [inv,dis,man,h]

	def findMoves(self,flex=False):
		limit = self.environment.sizes[0] - 1
		coords = self.coordinates()
		last = self.path[self.g]
		moves = []
		if coords[0] != 0 	  and (last != 'L' or flex): moves.append('R')
		if coords[0] != limit and (last != 'R' or flex): moves.append('L')
		if coords[1] != 0	  and (last != 'U' or flex): moves.append('D')
		if coords[1] != limit and (last != 'D' or flex): moves.append('U')
		return moves
	def moveTile(self, move):
		sequence = self.sequence
		width = self.environment.sizes[0]
		x = self.coordinates(self.coordinates())
		if move == 'R': y = x - 1
		if move == 'L': y = x + 1
		if move == 'D': y = x - width
		if move == 'U': y = x + width
		sequence[x] = sequence[y]
		sequence[y] = 0
	def valid(self):
		width = self.environment.sizes[0]
		self.inv,self.dis,self.man,self.h = self.details()
		inv = self.inv
		row = abs(self.coordinates()[1] - width)
		return True if (((width % 2 == 1) and (inv % 2 == 0)) or ((width % 2 == 0) and ((row % 2 == 1) == (inv % 2 == 0)))) else False
	def children(self):
		childList = []
		for move in self.moves:
			child = Taquin(self.environment,self,move)
			if child.h == 0: return child
			childList.append(child)
		return childList
	def magic(self, rand=0):
		length = self.environment.sizes[1]
		sequence = [0]*length
		for i in range(1, length): sequence[i-1] = i
		if rand == 1:
			shuffle(sequence)
			self.sequence = sequence
			while not self.valid():
				shuffle(sequence)
				self.sequence = sequence
		return sequence
	def __repr__(self):
		printable = ""
		printable += "\n"
		printable += "Taquin :\n"
		printable += ("|  seq. .. : {}\n").format(self.sequence)
		printable += ("|  path .. : {}\n").format(self.path)
		printable += ("|  inv. .. : {}\n").format(self.inv)
		printable += ("|  man. .. : {}\n").format(self.man)
		printable += ("|  moves . : {}\n").format(self.moves)
		printable += ("|  g ..... : {}\n").format(self.g)
		printable += ("|  h ..... : {}\n").format(self.h)
		printable += ("|  f ..... : {}\n").format(self.f)
		return printable


class Environment:
	def __init__(self,width,choices=None):
		self.sizes = (width,width*width)
		self.choices = choices
		self.weightings = self.getWeightings(choices)
		self.moves = [Taquin(self)]
		self.end = []
	def getWeightings(self,choices):
		if (choices == None): choices = [i for i in range(1,7)]
		weightings = []
		width = self.sizes[0]
		length = self.sizes[1] - 1
		pi = []
		for index in choices:
			rho = (4 if index % 2 != 0 else 1)
			if index == 1:
				if width == 3:
					pi = [36, 12, 12, 4, 1, 1, 4, 1]
			if index == 2 or index == 3:
				pi = [(length+1) - i for i in range(1,length+1)]
			if index == 4 or index == 5:
				pi = [0] * length
				weight = length
				for i in range(width-1):
					j = 0
					while pi[j] != 0:
						j += 1
					k = 0
					while k < width-i:
						pi[j] = weight
						j += 1
						weight -= 1
						k += 1
					j += i
					pi[j] = weight
					weight -= 1
					j += width
					while j < length - 1 :
						pi[j] = weight
						weight -= 1
						j += width
			if index == 6:
				pi = [1] * length
			if index == 7:
				pi = [0] * length
			if (len(pi)>0):
				weightings.append((pi,rho,index))
		return weightings
	def correct(self):
		for move in self.moves:
			move.inv,move.dis,move.man,move.h = move.details()
			move.f = move.g + move.h
	
	
	
	def aStar(self):
		print(self.moves[-1])
		queue = OrderedDict()
		queue[self.moves[-1].f] = [self.moves[-1]]
		while (True):
			k = list(queue.keys())[0]
			shouldBeExpanded = queue[k][0]
			del queue[k][0]
			if queue[k] == []: del queue[k]
			children = shouldBeExpanded.children()
			if isinstance(children,Taquin):
				print(children)
				self.end.append(children)
				return self.end[-1]
			else:
				for child in children :
					if(child.f in queue): queue[child.f].append(child)
					else: queue[child.f] = [child]
				queue = OrderedDict( sorted( queue.items(), key=lambda t: t[0]))
	

	
	def expand(self,function,decomposition=0):
		if (decomposition==0):
			print("\n\n")
			start = time.time()
			print(("Heuristiques utilisées : {}").format(self.choices))
			result = function()
			print(("Duration : {}").format(time.time() - start))
			print("\n\n")
			return result
		else:
			results = []
			decomposition = self.weightings.copy()
			for weighting in decomposition:
				print("\n")
				start = time.time()
				print(("Heuristiques utilisées : {}").format(weighting[2]))
				self.weightings = [weighting]
				self.correct()
				results.append(function())
				print(("Duration : {}").format(time.time() - start))
				print("\n\n.........................................\n")
			return results
	
	
	
	def play(self,move):
		self.moves.append(Taquin(self,self.moves[-1],move))
		return self.moves[-1]


class Fenetre(QWidget):

	def __init__(self,texte,mode):
		QWidget.__init__(self)
		self.texte = texte
		self.box = []
		self.mode = mode
		self.label3Present = False
		self.labelCoupsPresent = False
		self.LabelManhattanPresent = False
		self.LabelInvPresent = False
		self.LabelDisPresent = False
		self.h1state = False
		self.h2state = False
		self.h3state = False
		self.h4state = False
		self.h5state = False
		self.h6state = False
		self.heuristiques = []
		self.boutonEnCouleur = None

		#Chargement de la police inter bold
		id = QFontDatabase.addApplicationFont("/Users/melaniemarques/Downloads/Inter-3/Inter (TTF)/Inter-Bold.ttf")
		fontstr = QFontDatabase.applicationFontFamilies(id)[0]
		self.font = QFont(fontstr, 18)
		

		self.setWindowTitle("Taquin")
		self.resize(1000,500)
		self.setStyleSheet('background-color: rgb(252,252,252)')


		# Label
		label = QLabel('Settings : ', self)
		label.setFont(self.font)
		label.move(50,50)

		label2 = QLabel('Side Length : ',self)
		label2.setFont(QFont(fontstr, 14))
		label2.move(50,110)


		mode = QLabel('Mode : ',self)
		mode.setFont(QFont(fontstr, 14))
		mode.move(50,160)

		heuristiques = QLabel('Heuristics : ',self)
		heuristiques.setFont(QFont(fontstr,14))
		heuristiques.move(50,210)


		# ComboBox side length
		ComboBox = QComboBox(self)
		ComboBox.addItem("3 ")
		ComboBox.addItem("4 ")
		ComboBox.addItem("5 ")
		ComboBox.setStyleSheet('color: black;background-color: rgb(232,232,232);selection-background-color: rgb(255,255,255);')
		ComboBox.setFixedSize(QSize(85,20))
		ComboBox.move(150,110)
		ComboBox.activated[str].connect(self.selectionDimensions)
		#combo box choix Mode : 
		ComboBoxM = QComboBox(self)
		ComboBoxM.addItem("manual")
		ComboBoxM.addItem("pilot")
		ComboBoxM.setStyleSheet('color: black;background-color: rgb(232,232,232);selection-background-color: rgb(255,255,255)')
		ComboBoxM.setFixedSize(QSize(85,20))
		ComboBoxM.move(150,160)
		ComboBoxM.activated[str].connect(self.selectionMode)


		#Generate Button
		generate = QPushButton('Generate',self)
		generate.setFont(QFont(fontstr, 15))
		generate.setFixedSize(QSize(90,30))
		generate.setStyleSheet('color: rgb(179,179,179);background-color: rgb(232,232,232);border: none; border-radius: 4px;')
		generate.move(700,320)	
		generate.clicked.connect(self.appuiBoutonGenerate)


		#Bouton solution
		BoutonSolution = QPushButton('Solution',self)
		BoutonSolution.setFont(QFont(fontstr, 15))
		BoutonSolution.setFixedSize(QSize(115,30))
		BoutonSolution.setStyleSheet('color: rgb(179,179,179);background-color: rgb(232,232,232);border: none; border-radius: 4px;')
		BoutonSolution.move(805,320) 
		BoutonSolution.clicked.connect(self.Solution)

		#Check box des heuristiques : 
		h1 = QCheckBox('H.1',self)
		h1.setFont(QFont(fontstr,12))
		h1.move(150,210)
		h1.stateChanged.connect(self.selectionH1)

		h2 = QCheckBox('H.2',self)
		h2.setFont(QFont(fontstr,12))
		h2.move(150,235)
		h2.stateChanged.connect(self.selectionH2)

		h3 = QCheckBox('H.3',self)
		h3.setFont(QFont(fontstr,12))
		h3.move(150,260)
		h3.stateChanged.connect(self.selectionH3)

		h4 = QCheckBox('H.4',self)
		h4.setFont(QFont(fontstr,12))
		h4.move(195,210)
		h4.stateChanged.connect(self.selectionH4)

		h5 = QCheckBox('H.5',self)
		h5.setFont(QFont(fontstr,12))
		h5.move(195,235)
		h5.stateChanged.connect(self.selectionH5)

		h6 = QCheckBox('H.6',self)
		h6.setFont(QFont(fontstr,12))
		h6.move(195,260)
		h6.stateChanged.connect(self.selectionH6)

		self.show()

	def positionDansListe(self,liste,numero):
		"""Renvoie la position d'un élément dans une liste donnée si l'élément est présent dans la liste"""
		pos = 0
		for item in liste:
			if (item == numero):
				return pos
			pos+=1
		return None

	def ok(self):
		"""Renvoie les différents coups possibles (Right,Left,Down,Up) associés à la tuile à bouger sous forme de liste de liste [numéro de la tuile, coup]"""
		numeros = []
		cp = self.a.moves[-1].findMoves(True)
		print(cp)
		positionO = self.positionDansListe(self.a.moves[-1].sequence,0)
		
		for item in cp:
			if (item =="R"):
				numeros.append([self.a.moves[-1].sequence[positionO-1],'R'])
			if (item =="L"):
				numeros.append([self.a.moves[-1].sequence[positionO+1],'L'])
			if (item =="D"):
				numeros.append([self.a.moves[-1].sequence[positionO-int(self.texte)],'D'])
			if (item =="U"):
				numeros.append([self.a.moves[-1].sequence[positionO+int(self.texte)],'U'])
		return numeros
	

	def isItTheEnd(self):
		""" 
		Vérifie si on est dans un état final
		Cette fonction renvoie un booléen
		"""
		i = 0
		ok = True
		while(i<len(self.a.moves[-1].sequence)-1):
			if((i+1)!=self.a.moves[-1].sequence[i]): 
				ok = False
			i+=1
		return ok

	def operationColoration(self):
		"""Cette fonction colore la case associée au meilleur prochain coup dans le mode 'pilot'"""

		if(self.boutonEnCouleur!=None):
			self.boutonEnCouleur.setStyleSheet('color: rgb(170,170,170);background-color: rgb(238,238,238);border: none; border-radius: 4px;')
			self.boutonEnCouleur = None
		self.a.expand(self.a.aStar,0)
		caseAColorer = self.a.end[-1].path[self.nbCoupsJoues+1]
		verif = self.ok()
		i = 0
		while(i<len(verif)):
			if((self.mode == 'pilot')and(caseAColorer==verif[i][1])):
				numeroAColorer = verif[i][0]				
			i+=1
		for item in self.box:
			if(int(item.text())==numeroAColorer):						
				self.boutonEnCouleur = item
				self.boutonEnCouleur.setStyleSheet('color: rgb(255,255,255);background-color: rgb(135,206,250);border: none; border-radius: 4px;')

		
	def traductionEnFleches(self,codeATraduire):
		"""
		Traduit une solution en flèches : 
		- U (up) devient ↑
		- D (down) devient ↓
		- R (right) devient →
		- L (left) devient ←
		"""
		trad = ""
		for item in codeATraduire:
			if(item == 'R'):
				trad += '→'
			if(item == 'L'):
				trad+= '←'
			if(item =='U'):
				trad+='↑'
			if(item =='D'):
				trad+='↓'
		return trad

	def couic(self,chaineADecouper,nbCaracteres):
		""" Place des retour à la ligne dans une chaîne de caractères (chaineADecouper) tous les nbCaractères"""
		nouvelleChaine = ""
		k = 0
		while(k<len(chaineADecouper)):
			if(k<(len(chaineADecouper)-nbCaracteres)):
				nouvelleChaine += chaineADecouper[k:(k+nbCaracteres)]+"\n"
			else:
				nouvelleChaine += chaineADecouper[k:len(chaineADecouper)]
			k+=nbCaracteres
		return nouvelleChaine

	def appuiBoutonGenerate(self):
		if((len(self.heuristiques)!=0)and((self.mode=='pilot' and int(self.texte) == 3)or(self.mode=='manual'))):
			self.coupsJoues = ""
			self.nbCoupsJoues = 0
		#On supprime l'ancienne génération de taquin :
			if(self.label3Present!=False):
				self.label3.deleteLater()
				self.label3Present = False
		#On regarde si le label de coups est présent, si oui on le delete
			if(self.labelCoupsPresent!=False):
				self.labelNbCoupsJoues.clear()		
				self.labelCoupsPresent = False
		#On regarde si le label Manhattan est présent, si oui on le delete
			if(self.LabelManhattanPresent!=False):
				self.LabelManhattan.clear()			
				self.LabelManhattanPresent = False
		#On regarde si le label Inv est présent, si oui on le delete
			if(self.LabelInvPresent!=False):
				self.LabelInv.clear()			
				self.LabelInvPresent = False
		#On regarde si le label Dis est présent, si oui on le delete
			if(self.LabelDisPresent!=False):
				self.LabelDis.clear()			
				self.LabelDisPresent = False
		
		#On delete les boutons précédents du taquin : 		
			for k in self.box:
				k.deleteLater()
		
			self.box = []       
			self.fin= False
			DimTaquin = int(self.texte)
		
			self.a = Environment(DimTaquin,self.heuristiques)
			i = 0
			x = 0
			y = 0
	   #On génère les boutons du Taquin : 
			while(i<(DimTaquin*DimTaquin)):
				if(i%DimTaquin==0):
					x = 0
					y+=42
				if(self.a.moves[-1].sequence[i]!=0):
					BoutonGrille = QPushButton(str(self.a.moves[-1].sequence[i]),self)
					BoutonGrille.setFont(self.font)
					BoutonGrille.setFixedSize(QSize(40,40))
					BoutonGrille.setStyleSheet('color: rgb(170,170,170);background-color: rgb(238,238,238);border: none; border-radius: 4px;')
					BoutonGrille.move(700+x*42,1*y)
					self.box.append(BoutonGrille)
				x+=1
				i+=1

			for item in self.box:
				item.clicked.connect(self.appuiBoutonsTaquin)
				item.show()
			
			self.start_time = time.time()

			if(self.mode =='pilot'):
				self.operationColoration()

			if(int(self.texte)==3):
				self.a.expand(self.a.aStar,0)
				self.nbCoupsOpti = self.a.end[-1].g
				self.listeCoupsOpti = self.couic(self.traductionEnFleches(self.a.end[-1].path),20)

		elif(len(self.heuristiques)==0) :
			msg = QMessageBox.critical(self, 'ERROR', "Please enter heuristic(s).", QMessageBox.Ok)
		elif(self.mode=='pilot' and int(self.texte) != 3):
			msgPilot = QMessageBox.critical(self, 'ERROR', "Mode 'pilot' unvailable for side length higher than 3.", QMessageBox.Ok)
		


	
		
	def appuiBoutonsTaquin(self):
		if(self.fin!=True):
			#Nombre de coups effectues : 			
			ok = False
			#On récupère le numéro du bouton appuyé : 
			sender = self.sender()
			#on vérifie qu'on peut bouger le bouton			
			verif = self.ok() 
			i = 0
			move = "_"
			while(i<len(verif)):
				if(int(sender.text())==verif[i][0]):
					ok = True
					break
				i+=1

			#Si on peut bouger, on bouge le bouton : 
			if(ok == True):
				for item in self.box:
					if(item.text()==sender.text()):
						BoutonClique = item
						x = BoutonClique.x()
						y = BoutonClique.y()
					 
				if(verif[i][1]=='R'):
					BoutonClique.move(x+42,y)
					move = "R"     
				if(verif[i][1]=='L'):
					BoutonClique.move(x-42,y)
					move = "L"
				if(verif[i][1]=='U'):
					BoutonClique.move(x,y-42)
					move = "U"
				if(verif[i][1]=='D'):
					BoutonClique.move(x,y+42)
					move ="D" 
				self.a.play(move)
				self.coupsJoues+=move
				self.nbCoupsJoues +=1


			#Label nombre de coups joués
			self.labelNbCoupsJoues = QLabel("Coups:\n %d"%(self.a.moves[-1].g),self)
			self.labelNbCoupsJoues.setFont(self.font)
			self.labelNbCoupsJoues.setStyleSheet('background-color: rgb(238,238,238); border-radius: 4px;')
			self.labelNbCoupsJoues.setAlignment(Qt.AlignCenter)
			self.labelNbCoupsJoues.setFixedSize(QSize(110,50))
			self.labelNbCoupsJoues.move(50,320)
			self.labelNbCoupsJoues.show()
			self.labelCoupsPresent = True

			#Label Manhattan : 
			self.LabelManhattan = QLabel("Manhattan:\n%d"%(self.a.moves[-1].man),self)
			self.LabelManhattan.setFont(self.font)
			self.LabelManhattan.setStyleSheet('background-color: rgb(238,238,238); border-radius: 4px;')
			self.LabelManhattan.setAlignment(Qt.AlignCenter)
			self.LabelManhattan.setFixedSize(QSize(110,50))
			self.LabelManhattan.move(320,320)
			self.LabelManhattan.show()
			self.LabelManhattanPresent = True

			#Label Inv : 
			self.LabelInv = QLabel("Inversions:\n %d"%(self.a.moves[-1].inv),self)
			self.LabelInv.setFont(self.font)
			self.LabelInv.setStyleSheet('background-color: rgb(238,238,238); border-radius: 4px;')
			self.LabelInv.setAlignment(Qt.AlignCenter)
			self.LabelInv.setFixedSize(QSize(110,50))
			self.LabelInv.move(455,320)
			self.LabelInv.show()
			self.LabelInvPresent = True

			#Label Dis : 
			self.LabelDis = QLabel("Desordre:\n %d"%(self.a.moves[-1].dis),self)
			self.LabelDis.setFont(self.font)
			self.LabelDis.setStyleSheet('background-color: rgb(238,238,238); border-radius: 4px;')
			self.LabelDis.setAlignment(Qt.AlignCenter)
			self.LabelDis.setFixedSize(QSize(110,50))
			self.LabelDis.move(185,320)
			self.LabelDis.show()
			self.LabelDisPresent = True
			
			#On vérifie si on est dans l'état final :
			if(self.isItTheEnd()==True):
				self.fin = True
				for boutons in self.box:
					boutons.setStyleSheet('color: rgb(255,255,255);background-color: rgb(60,179,113);border: none; border-radius: 4px;')
					#perfs pour résoudre un taquin par le joueur:
				nbCoupsJoueur = self.nbCoupsJoues
				tempsMinute = int((time.time() - self.start_time)/60)
				tempsSecondes = int(time.time() - self.start_time)-tempsMinute*60
				coups = self.couic(self.traductionEnFleches(self.coupsJoues),20)
				if(int(self.texte)>3):
					msgResolition = QMessageBox.information(self, 'FELICITATION', "CONGRATULATIONS \n\nYou have solved the taquin in : \n- %d moves\n- %d minutes and %d seconds\n- this is your moves : %s"%(int(nbCoupsJoueur),int(tempsMinute),int(tempsSecondes),coups), QMessageBox.Ok)
				else:
					msgResolition2 = QMessageBox.information(self, 'FELICITATION', "CONGRATULATIONS \n\nYou have solved the taquin in : \n- %d moves\n- %d minutes and %d seconds\n- this is your moves : %s\n\n The minimal path is: \n- %d moves\n- path : \n%s"%(int(nbCoupsJoueur),int(tempsMinute),int(tempsSecondes),coups,int(self.nbCoupsOpti),self.listeCoupsOpti), QMessageBox.Ok)
		
			else:
				if(self.mode == 'pilot'):
					self.operationColoration()


	def Solution(self):
		if(len(self.box)!=0):
			if(self.label3Present!=False):
				self.label3.deleteLater()
				self.label3Present=False

			self.a.expand(self.a.aStar,0)
			self.solution = self.a.end[-1].path[self.nbCoupsJoues+1:len(self.a.end[-1].path)]
			self.solution = self.traductionEnFleches(self.solution)
			if(len(self.solution)>45):
				self.solution = self.couic(self.solution,45)

			self.label3 = QLabel("Solution : %s"%(self.solution),self)
			self.label3.setFont(self.font)
			self.label3.setStyleSheet('background-color: rgb(238,238,238); padding: 1em; border-radius: 4px;')
			self.label3.move(50,395)
			self.label3.show()

			self.label3Present = True

		else:
			msgSolution = QMessageBox.critical(self, 'ERROR', "Please generate a Taquin.", QMessageBox.Ok)
			

	def selectionDimensions(self,texte):
		self.texte = texte
	def selectionMode(self,mode):       
		self.mode = mode

	def selectionH1(self,state):
		if state == Qt.Checked:
			self.heuristiques.append(1)
		elif state != Qt.Checked:
			self.heuristiques.remove(1)

	def selectionH2(self,state):
		if state == Qt.Checked:
			self.heuristiques.append(2)			
		elif state != Qt.Checked:
			self.heuristiques.remove(2)

	def selectionH3(self,state):
		if state == Qt.Checked:
			self.heuristiques.append(3)		
		elif state != Qt.Checked:
			self.heuristiques.remove(3)

	def selectionH4(self,state):
		if state == Qt.Checked:
			self.heuristiques.append(4)				
		elif state != Qt.Checked:
			self.heuristiques.remove(4)

	def selectionH5(self,state):
		if state == Qt.Checked:
			self.heuristiques.append(5)			
		elif state != Qt.Checked:
			self.heuristiques.remove(5)

	def selectionH6(self,state):
		if state == Qt.Checked:
			self.heuristiques.append(6)			
		elif state != Qt.Checked:
			self.heuristiques.remove(6)
	

class __main__:
	app = QApplication.instance() 
	if not app:
		app = QApplication(sys.argv)

  
	fen = Fenetre('3','manual')
	fen.show()

	app.exec_()