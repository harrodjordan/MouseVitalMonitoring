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
from PyQt5.QtWidgets import QMainWindow, QAction, QMenu, QApplication, qApp, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QFrame, QSplitter, QStyleFactory, QLCDNumber, QLabel, QInputDialog



import numpy as np
import matplotlib.pyplot as plt
import time
		
plt.ion()

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import os, os.path
import random
import argparse
import sys
import csv
import scipy.io
import tkinter as tk
from tkinter import filedialog
from numpy import genfromtxt

# use patient monitoring systems as a design model 

import time
import os
import RPi.GPIO as GPIO
 
GPIO.setmode(GPIO.BCM)
DEBUG = 1
 
# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
def readadc(adcnum):

	SPICLK = 18
	SPIMISO = 23
	SPIMOSI = 24
	SPICS = 25

	GPIO.setup(SPIMOSI, GPIO.OUT)
	GPIO.setup(SPIMISO, GPIO.IN)
	GPIO.setup(SPICLK, GPIO.OUT)
	GPIO.setup(SPICS, GPIO.OUT)

	if ((adcnum > 7) or (adcnum < 0)):
			return -1

	GPIO.output(cspin, True)
 
	GPIO.output(clockpin, False)  # start clock low
	GPIO.output(cspin, False)     # bring CS low
 
	commandout = adcnum
	commandout |= 0x18  # start bit + single-ended bit
	commandout <<= 3    # we only need to send 5 bits here
	for i in range(5):
			if (commandout & 0x80):
					GPIO.output(mosipin, True)
			else:
					GPIO.output(mosipin, False)
			commandout <<= 1
			GPIO.output(clockpin, True)
			GPIO.output(clockpin, False)

	adcout = 0
	# read in one empty bit, one null bit and 10 ADC bits
	for i in range(12):
			GPIO.output(clockpin, True)
			GPIO.output(clockpin, False)
			adcout <<= 1
			if (GPIO.input(misopin)):
					adcout |= 0x1

	GPIO.output(cspin, True)
	
	adcout >>= 1       # first bit is 'null' so drop it
	return adcout*3.3/1023
 

# GPIO.setup(SPICS, GPIO.OUT)
 
# # 10k trim pot connected to adc #0
# potentiometer_adc = 0;
 
# last_read = 0       # this keeps track of the last potentiometer value
# tolerance = 5       # to keep from being jittery we'll only change
# 					# volume when the pot has moved more than 5 'counts'
 
# while True:
# 		# we'll assume that the pot didn't move
# 		trim_pot_changed = False
 
# 		# read the analog pin
# 		trim_pot = readadc(potentiometer_adc, SPICLK, SPIMOSI, SPIMISO, SPICS)
# 		# how much has it changed since the last read?
# 		pot_adjust = abs(trim_pot - last_read)
 
# 		if DEBUG:
# 				print "trim_pot:", trim_pot
# 				print "pot_adjust:", pot_adjust
# 				print "last_read", last_read
 
# 		if ( pot_adjust > tolerance ):
# 			   trim_pot_changed = True
 
# 		if DEBUG:
# 				print "trim_pot_changed", trim_pot_changed
 
# 		if ( trim_pot_changed ):
# 				set_volume = trim_pot / 10.24           # convert 10bit adc0 (0-1024) trim pot read into 0-100 volume level
# 				set_volume = round(set_volume)          # round out decimal value
# 				set_volume = int(set_volume)            # cast volume as integer
 
# 				print 'Volume = {volume}%' .format(volume = set_volume)
# 				set_vol_cmd = 'sudo amixer cset numid=1 -- {volume}% > /dev/null' .format(volume = set_volume)
# 				os.system(set_vol_cmd)  # set volume
 
# 				if DEBUG:
# 						print "set_volume", set_volume
# 						print "tri_pot_changed", set_volume
 
# 				# save the potentiometer reading for the next loop
# 				last_read = trim_pot
 
# 		# hang out and do nothing for a half second
# 		time.sleep(0.5)


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

	
		menubar = self.menuBar()
		fileMenu = menubar.addMenu('File')
		viewMenu = menubar.addMenu('View')
		recordingMenu = menubar.addMenu('Recording Options')

		self.statusbar = self.statusBar()
		self.statusbar.showMessage('Ready')
	
		impMenu = QMenu('Import', self)
		impAct = QAction('Import data', self) 
		impAct.triggered.connect(lambda: self.loadCsv)
		impMenu.addAction(impAct)

		expMenu = QMenu('Export', self)
		expAct = QAction('Export data', self) 
		expAct.triggered.connect(lambda: self.writeCsv)
		expMenu.addAction(expAct)
		
		newAct = QAction('New', self)       

		HRchangeWindowSize = QAction('Change HR Window Size', self)
		HRchangeWindowSize.triggered.connect(lambda: self.HRwindowSizeInput()) 

		resetWindow = QAction('Reset Window to Present', self)
		resetWindow.triggered.connect(lambda: self.windowReset())

		BRchangeWindowSize = QAction('Change BR Window Size', self)
		BRchangeWindowSize.triggered.connect(lambda: self.BRwindowSizeInput()) 

		TEMPchangeWindowSize = QAction('Change Temperature Window Size', self)
		TEMPchangeWindowSize.triggered.connect(lambda: self.TEMPwindowSizeInput()) 



		recordingMenu.addAction(HRchangeWindowSize)
		recordingMenu.addAction(BRchangeWindowSize)
		recordingMenu.addAction(TEMPchangeWindowSize)

		recordingMenu.addAction(resetWindow)

		
		fileMenu.addAction(newAct)
		fileMenu.addMenu(impMenu)
		fileMenu.addMenu(expMenu)
		fileMenu.addMenu(recordingMenu)

		#Making the status bar 

		viewStatAct = QAction('View statusbar', self, checkable=True)
		viewStatAct.setStatusTip('View statusbar')
		viewStatAct.setChecked(True)
		viewStatAct.triggered.connect(self.toggleMenu)
		viewMenu.addAction(viewStatAct)

		#Making the toolbar 

		exitAct = QAction(QIcon('cancel-512.png'), 'Exit', self)
		exitAct.setShortcut('Ctrl+Q')
		exitAct.triggered.connect(lambda: sys.exit())

		saveAct = QAction(QIcon('48-512.png'), 'Save', self)
		saveAct.setShortcut('Ctrl+S')
		saveAct.triggered.connect(lambda: self.saveData)

		importAct = QAction(QIcon('512x512.png'), 'Import', self)
		importAct.setShortcut('Ctrl+I')
		importAct.triggered.connect(lambda: self.saveData)

		exportAct = QAction(QIcon('document.png'), 'Export', self)
		exportAct.setShortcut('Ctrl+E')
		exportAct.triggered.connect(lambda: self.saveData)

		plotHRAct = QAction(QIcon('200px-Love_Heart_SVG.svg.png'), 'Record HR', self)
		plotHRAct.triggered.connect(lambda: self.lbl_HR.plot())

		plotBRAct = QAction(QIcon('980935_964a998538bc4052b413da77b99d4759~mv2.png'), 'Record BR', self)
		plotBRAct.triggered.connect(lambda: self.lbl_BR.plot())

		plotTempAct = QAction(QIcon('Screen Shot 2018-04-11 at 12.37.24 PM.png'), 'Record Temp', self)
		plotTempAct.triggered.connect(lambda: self.lbl_TEMP.plot())
		
		self.toolbar = self.addToolBar('Exit')
		self.toolbar = self.addToolBar('Save')
		self.toolbar = self.addToolBar('Import')
		self.toolbar = self.addToolBar('Export')
		self.toolbar = self.addToolBar('Record HR')
		self.toolbar = self.addToolBar('Record BR')
		self.toolbar = self.addToolBar('Record TEMP')

		self.toolbar.addAction(exitAct)
		self.toolbar.addAction(saveAct)
		self.toolbar.addAction(importAct)
		self.toolbar.addAction(exportAct)
		self.toolbar.addAction(plotHRAct)
		self.toolbar.addAction(plotBRAct)
		self.toolbar.addAction(plotTempAct)

		#Setting window size and showing
  
		self.show()

	def HRwindowSizeInput(self):

		# open a smaller window with a numerical input option 

		num,ok = QInputDialog.getInt(self,"HR Window Dialog","enter a number")
		
		if ok:
			newSize = num
			self.lbl_HR.plot(window=newSize, start = self.lbl_HR.current_time)

	def HRwindowSizeInput(self):

		# open a smaller window with a numerical input option 

		num,ok = QInputDialog.getInt(self,"BR Window Dialog","enter a number")
		
		if ok:
			newSize = num
			self.lbl_BR.plot(window=newSize, start = self.lbl_BR.current_time)

	def HRwindowSizeInput(self):

		# open a smaller window with a numerical input option 

		num,ok = QInputDialog.getInt(self,"Temperature Window Dialog","enter a number")
		
		if ok:
			newSize = num
			self.lbl_TEMP.plot(window=newSize, start = self.lbl_TEMP.current_time)


	def windowReset(self):

		self.lbl_HR.plot(window = self.lbl_HR.window, start = self.lbl_HR.current_time)
		self.lbl_BR.plot(window = self.lbl_BR.window, start = self.lbl_BR.current_time)
		self.lbl_TEMP.plot(window = self.lbl_TEMP.window, start = self.lbl_TEMP.current_time)


	
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
		


# TODO - manually adjustable sliding window, plot reset based on “start time”

class PlotCanvas(FigureCanvas):

	
 
	def __init__(self, parent=None, width=5, height=4, dpi=100, title=None, color='r-'):
		plt.ion()
		self.data = genfromtxt('example-data.csv', dtype=None, delimiter=',')
		self.fig = Figure(figsize=(width, height), dpi=dpi)
		self.color = color 
		self.title = title
		self.current_time = 0
		self.window = 50

		self.axes = self.fig.add_subplot(111)
 
		FigureCanvas.__init__(self, self.fig)
		self.setParent(parent)
 
		FigureCanvas.setSizePolicy(self,
				QtWidgets.QSizePolicy.Expanding,
				QtWidgets.QSizePolicy.Expanding)
		FigureCanvas.updateGeometry(self)
		self.fig.tight_layout(pad=3, w_pad=0.1, h_pad=0.1)
		#self.plot()
 
 
	def plot(self, pin):

		self.window = window 
		self.axes.set_title(self.title)

		for i in range(60):
			self.data = self.data.append(readadc(pin))
			pause(0.05)

		xtext = self.axes.set_xlabel('Time (s)') # returns a Text instance
		ytext = self.axes.set_ylabel('Volts (V)')
		line, = self.axes.plot(self.data[1:window, 0] ,self.data[1:window, 1], self.color)
		self.fig.canvas.draw_idle()
		self.fig.canvas.flush_events()
		plt.pause(0.05)

	
		for i in range(len(self.data)):
			self.data = self.data.append(readadc(pin))
			self.axes.set_ylim(min(self.data[i:window+i, 1]), max(self.data[i:window+i, 1]))
			self.axes.set_xlim(min(self.data[i:window+i, 0]), max(self.data[i:window+i, 0]))
			line.set_data(self.data[i:window+i, 0], self.data[i:window+i, 1])
			self.fig.canvas.draw_idle()
			self.fig.canvas.flush_events()
			plt.pause(0.05)
			self.current_time = i



	def plot(self, window=50, start=0):


		self.window = window 
		self.axes.set_title(self.title)

		xtext = self.axes.set_xlabel('Time (s)') # returns a Text instance
		ytext = self.axes.set_ylabel('Volts (V)')
		line, = self.axes.plot(self.data[1:window, 0] ,self.data[1:window, 1], self.color)
		self.fig.canvas.draw_idle()
		self.fig.canvas.flush_events()
		plt.pause(0.05)

	
		for i in range(len(self.data)):

			self.axes.set_ylim(min(self.data[i:window+i, 1]), max(self.data[i:window+i, 1]))
			self.axes.set_xlim(min(self.data[i:window+i, 0]), max(self.data[i:window+i, 0]))
			line.set_data(self.data[i:window+i, 0], self.data[i:window+i, 1])
			self.fig.canvas.draw_idle()
			self.fig.canvas.flush_events()
			plt.pause(0.05)
			self.current_time = i


	
		
		
if __name__ == '__main__':
	
	app = QApplication(sys.argv)
	ex = MainWindow()
	sys.exit(app.exec_())

