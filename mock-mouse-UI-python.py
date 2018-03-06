# Jordan Harrod
# BME 4080/4090: BME Senior Design 
# Rodent Vital Monitoring System 
# Client: Chris Schaffer and Daniel Rivera 

# February 9th, 2018

# Mock-Up of System UI for Demonstration Purposes 
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import PyQt5
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence, QIcon, QPixmap
from PyQt5.QtWidgets import QMainWindow, QAction, QMenu, QApplication, qApp, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QFrame, QSplitter, QStyleFactory, QLCDNumber, QLabel



import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
#import PIL.Image
import os, os.path
import random
import argparse
import sys
import csv

import tkinter

# use patient monitoring systems as a design model 

# TO DO BACKLOG - SPRINT 3
# set graph geometry to maintian size consistancy across instantiations 
# update the toolbar - import
# update the toolbar - export 
# data graphing
# how to connect pi to code
# connecting pi to code 
# display on touch screen 
# look into sensor integration 
# look into data reading 

# TO-DO 3.6.18


class MainWindow(QMainWindow):

	def __init__(self):

		super().__init__()

		self.left = 10
		self.top = 10
		self.title = 'Rodent Vitals Monitoring Software Demo'
		self.width = 1200
		self.height = 1200
		self.initUI()

	def initUI(self):  

		# Set Main Window Geometry and Title

		self.setGeometry(self.left, self.top, self.width, self.height)
		self.setWindowTitle(self.title)  



		#TEMPORARY file name for data import - will be replaced with import system 

		fileName='/Users/jordanharrod/Desktop/test-data.csv'



		#LCDs for numerical vital monitoring 



		lcd_BR = QLCDNumber(self)
		lcd_BR.setSegmentStyle(QLCDNumber.Flat)
		paletteBR = lcd_BR.palette()
		paletteBR.setColor(paletteBR.WindowText, QtGui.QColor(85, 85, 240))
		lcd_BR.setPalette(paletteBR)

		lcd_HR = QLCDNumber(self)
		lcd_HR.setSegmentStyle(QLCDNumber.Flat)
		paletteHR = lcd_HR.palette()
		paletteHR.setColor(paletteHR.WindowText, QtGui.QColor(85, 255, 85))
		lcd_HR.setPalette(paletteHR)

		lcd_TEMP = QLCDNumber(self)
		lcd_TEMP.setSegmentStyle(QLCDNumber.Flat)
		paletteTEMP = lcd_TEMP.palette()
		paletteTEMP.setColor(paletteTEMP.WindowText, QtGui.QColor(255, 85, 85))
		lcd_TEMP.setPalette(paletteTEMP)



		#Labels for vitals 


		BRlabel = QLabel('Breathing Rate (breaths/min)')
		HRlabel = QLabel('Heart Rate (beats/min)')
		TEMPlabel = QLabel('Subject Temperature (Celsius)')



		#Matplotlib graphs 

		lbl_TEMP = PlotCanvas(title='Subject Temperature (Celsius)', color='r-')
		lbl_HR = PlotCanvas(title='Heart Rate (beats/min)', color='g-')
		lbl_BR = PlotCanvas(title='Breathing Rate (breaths/min)', color='b-')



		#Setting up Frame Layout 

		wid = QWidget(self)
		self.setCentralWidget(wid)

		box = QHBoxLayout(self)




		#Boxes for LCD vitals 

		box_HRLCD = QHBoxLayout(self)
		box_BRLCD = QHBoxLayout(self)
		box_TEMPLCD = QHBoxLayout(self)

		box_HRLCD.addWidget(lcd_HR)
		box_BRLCD.addWidget(lcd_BR)
		box_TEMPLCD.addWidget(lcd_TEMP)


		box_HRgraph = QHBoxLayout(self)
		box_BRgraph = QHBoxLayout(self)
		box_TEMPgraph = QHBoxLayout(self)

		box_HRgraph.addWidget(lbl_HR)
		box_BRgraph.addWidget(lbl_BR)
		box_TEMPgraph.addWidget(lbl_TEMP)




		# Frames for vitals 

		topleft = QFrame(self)
		topleft.setFrameShape(QFrame.Box)

		topright = QFrame(self)
		topright.setFrameShape(QFrame.Box)

		middleleft = QFrame(self)
		middleleft.setFrameShape(QFrame.Box)

		middleright = QFrame(self)
		middleright.setFrameShape(QFrame.Box)

		bottomleft = QFrame(self)
		bottomleft.setFrameShape(QFrame.Box)

		bottomright = QFrame(self)
		bottomright.setFrameShape(QFrame.Box)

		topleft.setLayout(box_HRgraph)
		topright.setLayout(box_HRLCD)

		middleleft.setLayout(box_BRgraph)
		middleright.setLayout(box_BRLCD)

		bottomleft.setLayout(box_TEMPgraph)
		bottomright.setLayout(box_TEMPLCD)





		# Splitting frames and adding layout to window 


		splitter1 = QSplitter(Qt.Horizontal)
		splitter1.addWidget(topleft)
		splitter1.addWidget(topright)

		splitter2 = QSplitter(Qt.Horizontal)
		splitter2.addWidget(middleleft)
		splitter2.addWidget(middleright)

		splitter3 = QSplitter(Qt.Horizontal)
		splitter3.addWidget(bottomleft)
		splitter3.addWidget(bottomright)

		splitter4 = QSplitter(Qt.Vertical)
		splitter4.addWidget(splitter1)
		splitter4.addWidget(splitter2)
		splitter4.addWidget(splitter3)

		box.addWidget(splitter4)
		wid.setLayout(box)    

		#UNFINISHED BELOW


		#Making the menu bar  
	
		menubar = self.menuBar()
		fileMenu = menubar.addMenu('File')
		viewMenu = menubar.addMenu('View')

		self.statusbar = self.statusBar()
		self.statusbar.showMessage('Ready')
	
		impMenu = QMenu('Import', self)
		impAct = QAction('Import data', self) 
		impAct.triggered.connect(self.loadCsv)
		impMenu.addAction(impAct)

		expMenu = QMenu('Export', self)
		expAct = QAction('Export data', self) 
		expAct.triggered.connect(self.writeCsv)
		expMenu.addAction(expAct)
		
		newAct = QAction('New', self)        
		
		fileMenu.addAction(newAct)
		fileMenu.addMenu(impMenu)
		fileMenu.addMenu(expMenu)

		#Making the status bar 

		viewStatAct = QAction('View statusbar', self, checkable=True)
		viewStatAct.setStatusTip('View statusbar')
		viewStatAct.setChecked(True)
		viewStatAct.triggered.connect(self.toggleMenu)
		viewMenu.addAction(viewStatAct)

		#Making the toolbar 

		exitAct = QAction(QIcon('exit24.png'), 'Exit', self)
		exitAct.setShortcut('Ctrl+Q')
		exitAct.triggered.connect(qApp.quit)
		
		self.toolbar = self.addToolBar('Exit')
		self.toolbar.addAction(exitAct)

		#Setting window size and showing
  
		self.show()


	
	def toggleMenu(self, state):
		
		if state:
			self.statusbar.show()
		else:
			self.statusbar.hide()

	# update import export functionality 

	def loadCsv(self, fileName):

		with open(fileName, "rb") as fileInput:

			for row in csv.reader(fileInput): 

				items = [
					QtGui.QStandardItem(field)
					for field in row
				]
				self.model.appendRow(items)

		self.graph.plot(PlotDataItem(xValues, yValues))


	def writeCsv(self, fileName):

		with open(fileName, "wb") as fileOutput:

			writer = csv.writer(fileOutput)

			for rowNumber in range(self.model.rowCount()):
				fields = [
					self.model.data(
						self.model.index(rowNumber, columnNumber),
						QtCore.Qt.DisplayRole
					)
					for columnNumber in range(self.model.columnCount())
				]

				writer.writerow(fields)


# TODO - Implement these methods 

	# def analyzeHR(self):

		



	# def analyzeBR(self):

		


	# def analyzeTEMP(self):

		


# TODO - Change graph layout to have axes meet edges with title at the top  - Change graph colors to match patient monitoring systems 

class PlotCanvas(FigureCanvas):
 
	def __init__(self, parent=None, width=5, height=4, dpi=100, title=None, color='r-'):
		fig = Figure(figsize=(width, height), dpi=dpi)
		self.color = color 
		self.title = title
		self.axes = fig.add_subplot(111)
 
		FigureCanvas.__init__(self, fig)
		self.setParent(parent)
 
		FigureCanvas.setSizePolicy(self,
				QtWidgets.QSizePolicy.Expanding,
				QtWidgets.QSizePolicy.Expanding)
		FigureCanvas.updateGeometry(self)
		self.plot()
 
 
	def plot(self, ):
		data = [random.random() for i in range(25)]
		ax = self.figure.add_subplot(111)
		ax.plot(data, self.color)
		ax.set_title(self.title)
		self.draw()



	
		
		
if __name__ == '__main__':
	
	app = QApplication(sys.argv)
	ex = MainWindow()
	sys.exit(app.exec_())

