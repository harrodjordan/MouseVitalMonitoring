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
import scipy.signal as signal
from numpy import genfromtxt
import pandas as pd
import pywt
from collections import deque

def WaveletTransform(data):
	cA, cD = pywt.dwt(data, 'db4')
	return cA

# use patient monitoring systems as a design model 


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


		self.lbl = PlotCanvas()


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
		self.lcd_BR.display(58)


		
		self.lcd_HR.setSegmentStyle(QLCDNumber.Flat)
		paletteHR = self.lcd_HR.palette()
		paletteHR.setColor(paletteHR.WindowText, QtGui.QColor(85, 255, 85))
		self.lcd_HR.setPalette(paletteHR)
		self.lcd_HR.display(287)

		
		self.lcd_TEMP.setSegmentStyle(QLCDNumber.Flat)
		paletteTEMP = self.lcd_TEMP.palette()
		paletteTEMP.setColor(paletteTEMP.WindowText, QtGui.QColor(255, 85, 85))
		self.lcd_TEMP.setPalette(paletteTEMP)
		self.lcd_TEMP.display(17)



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


		box_graph = QHBoxLayout(self)

		box_graph.addWidget(self.lbl)



		# Frames for vitals 

		left = QFrame(self)
		left.setFrameShape(QFrame.Box)

		topright = QFrame(self)
		topright.setFrameShape(QFrame.Box)

		middleright = QFrame(self)
		middleright.setFrameShape(QFrame.Box)

		bottomright = QFrame(self)
		bottomright.setFrameShape(QFrame.Box)

		left.setLayout(box_graph)
		topright.setLayout(box_HRLCD)

		middleright.setLayout(box_BRLCD)


		bottomright.setLayout(box_TEMPLCD)


		# Splitting frames and adding layout to window 


		splitter1 = QSplitter(Qt.Vertical)
		splitter1.addWidget(topright)
		splitter1.addWidget(middleright)

		splitter2 = QSplitter(Qt.Vertical)
		splitter2.addWidget(splitter1)
		splitter2.addWidget(bottomright)

		splitter3 = QSplitter(Qt.Horizontal)
		splitter3.addWidget(left)
		splitter3.addWidget(splitter2)


		box.addWidget(splitter3)
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

		changeWindowSize = QAction('Change Window Size', self)
		changeWindowSize.triggered.connect(lambda: self.windowSizeInput()) 

		resetWindow = QAction('Reset Window to Present', self)
		resetWindow.triggered.connect(lambda: self.windowReset())



		recordingMenu.addAction(changeWindowSize)

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
		exitAct.triggered.connect(lambda: sys.exit())

		exportAct = QAction(QIcon('512x512.png'), 'Export Vitals', self)
		exportAct.triggered.connect(lambda: self.writeRealCsv())

		exportRawAct = QAction(QIcon('document.png'), 'Export Raw Data', self)
		exportRawAct.triggered.connect(lambda: self.writeVoltageCsv())

		startAct = QAction(QIcon('graphs icon.png'), 'Start Graphs', self)
		startAct.triggered.connect(lambda: self.lbl.plot(self.lcd_HR, self.lcd_BR, self.lcd_TEMP))

		heatAct = QAction(QIcon('temperature icon.png'), 'Start Temperature', self)
		heatAct.triggered.connect(lambda: self.tempControl())

		vitalsAct = QAction(QIcon('vitals icon.png'), 'Start Vitals', self)
		vitalsAct.triggered.connect(lambda: self.startVitals())

		
		self.toolbar = self.addToolBar('Exit')
		self.toolbar = self.addToolBar('Save')
		self.toolbar = self.addToolBar('Export')
		self.toolbar = self.addToolBar('Export')

		self.toolbar.addAction(exitAct)
		self.toolbar.addAction(startAct)
		self.toolbar.addAction(heatAct)
		self.toolbar.addAction(vitalsAct)
		self.toolbar.addAction(exportAct)


		#Setting window size and showing
  
		self.show()

	def analyzeHR(self, run=True):

		data = genfromtxt('breathdata.csv', dtype=None, delimiter=',')
		
		HR_ADCchan = 1

		run = True 

		all_data = []
		all_hr = []

		count = 0

		while run: 

			Value = []
			HR = []

			HR_Wave = WaveletTransform(data[1+count:5000+count])
			peakind = signal.find_peaks_cwt(HR_Wave, np.arange(1,1000))

			dist = []


			for i in range(len(peakind)-2):

				dist.append(peakind[i+1] - peakind[i])

			heart_rate = np.mean(1./np.sum(dist))
			self.lcd_HR.display(heart_rate)
			all_hr.append(heart_rate)

			count = count + 10
			print(heart_rate)





	def startVitals(self):

		t = []

		vital_thread = threading.Thread(target = self.analyzeHR())
		t.append(vital_thread)
		vital_thread.start()

		#temp_thread = threading.Thread(self.tempControl())
		plot_thread = threading.Thread(target = self.lbl.plot())
		

		t.append(plot_thread)
		

		#temp_thread.start()
		plot_thread.start()
		#plot_thread.run()
		
		#vital_thread.run()


		

	def windowSizeInput(self):

		# open a smaller window with a numerical input option 

		num,ok = QInputDialog.getInt(self,"Window Dialog","enter a number")
		
		if ok:
			newSize = num
			self.lbl.plot(window=newSize, start = self.lbl.current_time)


	def windowReset(self):

		self.lbl.plot(window = self.lbl.window, start = self.lbl.current_time)
	
	def toggleMenu(self, state):
		
		if state:
			self.statusbar.show()
		else:
			self.statusbar.hide()

	# IN PROGRESS - last line of loadCSV needs to be changed and graphs need to be made self variables upon initialization for dynamic changing and one for models for each vital

	def writeVoltageCsv(self):
		cwd = os.getcwd()

		volt_hr = self.lbl.volt_hr
		volt_br = self.lbl.volt_br
		volt_temp = self.lbl.volt_temp

		fileName_volt = cwd + "/Voltage_Data.csv"
		

		data = pd.DataFrame({'Heart Rate (V)':volt_hr, 'Breathing Rate (V)':volt_br, 'Temperature (V)':volt_temp})
		data.to_csv(fileName_volt, index=False)

	def writeRealCsv(self):
		cwd = os.getcwd()
		real_hr = self.lbl.real_hr
		real_br = self.lbl.real_br
		real_temp = self.lbl.real_temp

		fileName_real = cwd + "/Vital_Data.csv"

		data = pd.DataFrame({'Heart Rate (bpm)':real_hr, 'Breathing Rate (bpm)':real_temp, 'Temperature (F)':real_temp})
		data.to_csv(fileName_real, index=False)

# TODO - manually adjustable sliding window, plot reset based on “start time”

class PlotCanvas(FigureCanvas):

	def __init__(self, parent=None, width=5, height=4, dpi=100, title=None, color='r-'):

		plt.ion()

		self.fig = Figure(figsize=(width, height), dpi=dpi)
		self.color = color 
		self.title = title
		self.current_time = 0
		self.window = 10000

		self.HR = self.fig.add_subplot(311)
		self.BR = self.fig.add_subplot(312)
		self.Temp = self.fig.add_subplot(313)

		self.data_hr = genfromtxt('breathdata.csv', dtype=None, delimiter=',')
		self.data_br = genfromtxt('heartdata.csv', dtype=None, delimiter=',')
		self.data_temp = genfromtxt('faketemp2.csv', dtype=None, delimiter=',')
		self.data = genfromtxt('timedata.csv', dtype=None, delimiter=',')

		self.hr_y = deque([0.0]*self.window)
		self.br_y = deque([0.0]*self.window)
		self.temp_y = deque([0.0]*self.window)
		self.x = deque([0.0]*self.window)

		self.hr_data = []
		self.br_data = []
		self.temp_data = []

		self.time_data = []

		self.hr_volt = []
		self.br_volt = []
		self.temp_volt = []

		self.start = 0
 
		FigureCanvas.__init__(self, self.fig)
		self.setParent(parent)
 
		FigureCanvas.setSizePolicy(self,
				QtWidgets.QSizePolicy.Expanding,
				QtWidgets.QSizePolicy.Expanding)
		FigureCanvas.updateGeometry(self)
		self.fig.tight_layout(pad=1, w_pad=0.1, h_pad=0.1)
		self.count = 0


		print("Initializing PlotCanvas")

	def crosstalk(self):

	    HR_iter = iter(self.hr_y)
	    BR_iter = iter(self.br_y)

	    for i in range(50):

	        self.br_y.popleft()
	        self.br_y.append((self.br_y[i]-self.hr_y[i]))


	def addToBuf(self, buf, val):

		if len(buf) < self.window:
			buf.append(val)
		else:
			buf.popleft()
			buf.append(val)

  # add data
	def add(self, buf, volts, chan, time_check = False):

		if time_check == True:

			self.addToBuf(buf, (self.data[self.count+1]))

		else:
	

			if chan == 0:
			
				self.addToBuf(buf, self.data_br[self.count+1])

			if chan == 1: 

				self.addToBuf(buf, self.data_hr[self.count+1])

		self.count = self.count+1




	def analyzeHR(self):

		Value = []
		HR = []


		peakind, _ = signal.find_peaks(self.hr_y, prominence = 0.15, distance = 150)


		dist = []


		for i in range(len(peakind) - 2):

			dist = np.append(dist ,(peakind[i+1] - peakind[i])/1000)

		heart_rate = np.mean(60/np.array(dist)) 
		self.hr_data.append(heart_rate)

		return heart_rate



		# see if you need to charge the GPIO channels before sampling 

	def analyzeBR(self):


		Value = []
		BR = []

		peakind, _ = signal.find_peaks(self.br_y, prominence = 0.30, distance = 500) #300 

		dist = []
		for i in range(len(peakind) - 2):

			dist = np.append(dist, (peakind[i+1] - peakind[i])/1000)

		breath_rate = np.mean(60/np.array(dist))
		self.br_data.append(breath_rate)

		print(peakind)

		return breath_rate


	def plot(self, lcd_HR, lcd_BR, lcd_TEMP, window=50, start=0):

		self.start = time.time()

		self.window = window 
		self.HR.set_title('Heart Rate')
		self.BR.set_title('Breathing Rate')
		self.Temp.set_title('Current Temperature')

		xtext_hr = self.HR.set_xlabel('Time (s)') # returns a Text instance
		ytext_hr = self.HR.set_ylabel('Volts (V)')

		xtext_br = self.BR.set_xlabel('Time (s)') # returns a Text instance
		ytext_br = self.BR.set_ylabel('Volts (V)')

		xtext_temp = self.Temp.set_xlabel('Time (s)') # returns a Text instance
		ytext_temp = self.Temp.set_ylabel('Volts (V)')

		line_hr, = self.HR.plot(self.x ,self.hr_y, '-g')
		line_br, = self.BR.plot(self.x ,self.br_y,  '-c')
		line_temp, = self.Temp.plot(self.x, self.temp_y, '-r')

		self.fig.canvas.draw_idle()
		self.fig.canvas.flush_events()

		count = 0;

	
		while True:

			diff = time.time()

			lcd_BR.setSegmentStyle(QLCDNumber.Flat)
			lcd_TEMP.setSegmentStyle(QLCDNumber.Flat)



			current_hr = self.analyzeHR()
			current_br = self.analyzeBR()


			lcd_HR.display(current_hr)
			lcd_BR.display(current_br)



			for i in range(500):

				self.add(self.x, self.time_data, 0, time_check = True)
				self.add(self.hr_y, self.hr_volt, 0)
				self.add(self.br_y, self.br_volt, 1)

			#self.crosstalk()

			self.HR.set_ylim(min(self.hr_y), max(self.hr_y))
			self.HR.set_xlim(min(self.x), max(self.x))
			line_hr.set_data(self.x, self.hr_y)

			self.BR.set_ylim(min(self.br_y), max(self.br_y))
			self.BR.set_xlim(min(self.x), max(self.x))
			line_br.set_data(self.x, self.br_y)


			self.Temp.set_ylim(min(self.temp_y), max(self.temp_y))
			self.Temp.set_xlim(min(self.x), max(self.x))
			line_temp.set_data(self.x, self.temp_y)


			self.fig.canvas.draw_idle()
			

			self.fig.canvas.flush_events()

			plt.show()

			

			self.current_time = time.time()

			print("Time to loop")

			print(diff - self.current_time)

			count = count + 1

		plt.show()


class PID:


	def __init__(self, P=2.0, I=0.0, D=1.0, Derivator=0, Integrator=0, Integrator_max=500, Integrator_min=-500):

		self.Kp=P
		self.Ki=I
		self.Kd=D
		self.Derivator=Derivator
		self.Integrator=Integrator
		self.Integrator_max=Integrator_max
		self.Integrator_min=Integrator_min

		self.set_point=0.0
		self.error=0.0

		print("Initializing PID")

	def update(self,current_value):
		"""
		Calculate PID output value for given reference input and feedback
		"""

		self.error = self.set_point - current_value

		self.P_value = self.Kp * self.error
		self.D_value = self.Kd * ( self.error - self.Derivator)
		self.Derivator = self.error

		self.Integrator = self.Integrator + self.error

		if self.Integrator > self.Integrator_max:
			self.Integrator = self.Integrator_max
		elif self.Integrator < self.Integrator_min:
			self.Integrator = self.Integrator_min

		self.I_value = self.Integrator * self.Ki

		PID = self.P_value + self.I_value + self.D_value

		return PID

	def setPoint(self,set_point):
		"""
		Initilize the setpoint of PID
		"""
		self.set_point = set_point
		self.Integrator=0
		self.Derivator=0
	
		
		
if __name__ == '__main__':
	
	app = QApplication(sys.argv)
	ex = MainWindow()
	sys.exit(app.exec_())

