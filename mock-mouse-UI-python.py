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
import tkinter as tk
from tkinter import filedialog

# use patient monitoring systems as a design model 

# TO DO BACKLOG - SPRINT 3

# data graphing
# how to connect pi to code
# connecting pi to code 
# display on touch screen 
# look into sensor integration 
# look into data reading 




class MainWindow(QMainWindow):

	def __init__(self):

		super().__init__()

		self.left = 10
		self.top = 10
		self.title = 'Rodent Vitals Monitoring Software Demo'
		self.width = 1200
		self.height = 1200
		self.model = [] 

		#Matplotlib graphs 


		self.lbl_TEMP = PlotCanvas(title='Subject Temperature (Celsius)', color='r-')
		self.lbl_HR = PlotCanvas(title='Heart Rate (beats/min)', color='g-')
		self.lbl_BR = PlotCanvas(title='Breathing Rate (breaths/min)', color='b-')

		#LCDs for numerical vital monitoring 

		self.lcd_BR = QLCDNumber(self)
		self.lcd_HR = QLCDNumber(self)
		self.lcd_TEMP = QLCDNumber(self)

		self.initUI()

	def initUI(self):  

		# Set Main Window Geometry and Title

		self.setGeometry(self.left, self.top, self.width, self.height)
		self.setWindowTitle(self.title)  



		#LCDs for numerical vital monitoring 

		
		self.lcd_BR.setSegmentStyle(QLCDNumber.Flat)
		paletteBR = self.lcd_BR.palette()
		paletteBR.setColor(paletteBR.WindowText, QtGui.QColor(85, 85, 240))
		self.lcd_BR.setPalette(paletteBR)

		
		self.lcd_HR.setSegmentStyle(QLCDNumber.Flat)
		paletteHR = self.lcd_HR.palette()
		paletteHR.setColor(paletteHR.WindowText, QtGui.QColor(85, 255, 85))
		self.lcd_HR.setPalette(paletteHR)

		
		self.lcd_TEMP.setSegmentStyle(QLCDNumber.Flat)
		paletteTEMP = self.lcd_TEMP.palette()
		paletteTEMP.setColor(paletteTEMP.WindowText, QtGui.QColor(255, 85, 85))
		self.lcd_TEMP.setPalette(paletteTEMP)



		#Labels for vitals 


		BRlabel = QLabel('Breathing Rate (breaths/min)')
		HRlabel = QLabel('Heart Rate (beats/min)')
		TEMPlabel = QLabel('Subject Temperature (Celsius)')


		#Setting up Frame Layout 

		wid = QWidget(self)
		self.setCentralWidget(wid)

		box = QHBoxLayout(self)


		#Boxes for LCD vitals 

		box_HRLCD = QHBoxLayout(self)
		box_BRLCD = QHBoxLayout(self)
		box_TEMPLCD = QHBoxLayout(self)

		box_HRLCD.addWidget(self.lcd_HR)
		box_BRLCD.addWidget(self.lcd_BR)
		box_TEMPLCD.addWidget(self.lcd_TEMP)


		box_HRgraph = QHBoxLayout(self)
		box_BRgraph = QHBoxLayout(self)
		box_TEMPgraph = QHBoxLayout(self)

		box_HRgraph.addWidget(self.lbl_HR)
		box_BRgraph.addWidget(self.lbl_BR)
		box_TEMPgraph.addWidget(self.lbl_TEMP)




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

		exitAct = QAction(QIcon('cancel-512.png'), 'Exit', self)
		exitAct.setShortcut('Ctrl+Q')
		exitAct.triggered.connect(qApp.quit)

		saveAct = QAction(QIcon('48-512.png'), 'Save', self)
		saveAct.setShortcut('Ctrl+S')
		saveAct.triggered.connect(self.saveData)

		importAct = QAction(QIcon('512x512.png'), 'Import', self)
		importAct.setShortcut('Ctrl+I')
		importAct.triggered.connect(self.saveData)

		exportAct = QAction(QIcon('document.png'), 'Export', self)
		exportAct.setShortcut('Ctrl+E')
		exportAct.triggered.connect(self.saveData)
		
		self.toolbar = self.addToolBar('Exit')
		self.toolbar = self.addToolBar('Save')
		self.toolbar = self.addToolBar('Import')
		self.toolbar = self.addToolBar('Export')

		self.toolbar.addAction(exitAct)
		self.toolbar.addAction(saveAct)
		self.toolbar.addAction(importAct)
		self.toolbar.addAction(exportAct)

		#Setting window size and showing
  
		self.show()


	
	def toggleMenu(self, state):
		
		if state:
			self.statusbar.show()
		else:
			self.statusbar.hide()

	# IN PROGRESS - last line of loadCSV needs to be changed and graphs need to be made self variables upon initialization for dynamic changing and one for models for each vital

	def loadCsv(self):

		root = tk.Tk()
		root.withdraw()

		fileName = filedialog.askopenfilename(filetypes=(("csv files","*.csv"), ("xls files","*.xls"), ("xlsx files","*.xlsx"), ("txt files","*.txt"), ("all files","*.*")))

		with open(fileName, "rb") as fileInput:

			for row in csv.reader(fileInput): 

				items = [
					QtGui.QStandardItem(field)
					for field in row
				]
				self.model.appendRow(items)

		writeCsv(fileName)

		self.lbl_HR.plot([self.model[1], self.model[2]])
		self.lbl_BR.plot([self.model[1], self.model[3]])
		self.lbl_TEMP.plot([self.model[1], self.model[4]])


	def writeCsv(self, fileName):

		cwd = os.getcwd()

		fileName = cwd + fileName

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

	def saveData(self):

		data = self.model

	def exportData(self):

		data = self.model 


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
		fig.tight_layout(pad=3, w_pad=0.1, h_pad=0.1)
		self.plot()
 
 
	def plot(self, data):
		ax = self.figure.add_subplot(111)
		ax.plot(data, self.color)
		ax.set_title(self.title)
		xtext = ax.set_xlabel('Time (s)') # returns a Text instance
		ytext = ax.set_ylabel('Volts (mV)')
		ax.autoscale(enable=True, axis='x', tight=True)

		[m, n] = np.size(data)

		for i in range(n):
    		ax.plot(data(1:i), self.color)
    		plt.draw()
    		plt.pause(0.05)

		while True:
    		plt.pause(0.05)
			self.draw()

	def plot(self):
		data = [random.random() for i in range(25)]
		ax = self.figure.add_subplot(111)
		ax.plot(data, self.color)
		ax.set_title(self.title)
		xtext = ax.set_xlabel('Time (s)') # returns a Text instance
		ytext = ax.set_ylabel('Volts (mV)')
		ax.autoscale(enable=True, axis='x', tight=True)
		self.draw()



	
		
		
if __name__ == '__main__':
	
	app = QApplication(sys.argv)
	ex = MainWindow()
	sys.exit(app.exec_())

