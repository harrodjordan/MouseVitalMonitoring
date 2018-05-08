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

import spidev 
import time 
import os
import pywt 
import scipy
from scipy import signal 
import Adafruit_GPIO.SPI as SPI
import 	Adafruit_Python_MCP3008.Adafruit_MCP3008 as Adafruit_MCP3008 
import pandas as pd
from collections import deque
import RPi.GPIO as GPIO

#Import the MCP4725 module.
import Adafruit_Python_MCP4725.Adafruit_MCP4725 as  Adafruit_Python_MCP4725
# Create a DAC instance.
dac = Adafruit_Python_MCP4725.MCP4725()

print("Initializing ADC Direction Pin")

SPI_PORT=0
SPI_DEVICE=0

GPIO.setmode(GPIO.BOARD)

GPIO.setup(13, GPIO.OUT)
print("Initializing PWM Pin")




mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))


def ReadChannel(chan):
	if((chan<0) or (chan>7)):
		return -1

	data = mcp.read_adc(chan)
	return data 

def ConvertVolts(data, places):
	volts = (data * 3.3)/1023
	volts = round(volts, places)
	return volts 

def ConvertTemp(data, places):
	reading = (4095 / data)  - 1;     
	temp = 10000 / reading + 20; 
	temp = round(temp, places)
	return temp 

def WaveletTransform(data):
	cA, cD = pywt.dwt(data, 'db4')
	return cA

#channel 0 = HR
#channel 1 = BR
#channel 2 = Temp 
#channel 3 = direction - NOT READING IN 

#GPIO5 = toggle pzt 


import numpy as np
import matplotlib.pyplot as plt
import time
		


from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import os, os.path
import random
import argparse
import sys
import csv

from numpy import genfromtxt

# use patient monitoring systems as a design model 

import time
import os

 

class MainWindow(QMainWindow):


	def __init__(self):

		super().__init__()

		self.left = 10
		self.top = 10
		self.title = 'Rodent Vitals Monitoring Software Demo'
		self.width = 700
		self.height = 500
		self.model = [] 

		#Matplotlib graphs 


		self.lbl = PlotCanvas()

		#LCDs for numerical vital monitoring 

		self.lcd_BR = QLCDNumber(self)
		self.lcd_HR = QLCDNumber(self)
		self.lcd_TEMP = QLCDNumber(self)

		self.p = GPIO.PWM(13, 10000)  # channel=5 frequency=1kHz
		self.control = PID()
		self.control.setPoint(set_point=37)
		self.p.start(0)

		print("Initializing MainWindow")


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


		box_graph = QHBoxLayout(self)

		box_graph.addWidget(self.lbl)


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

		exportAct = QAction(QIcon('document.png'), 'Export Vitals', self)
		exportAct.triggered.connect(lambda: self.writeRealCsv())

		exportRawAct = QAction(QIcon('document.png'), 'Export Raw Data', self)
		exportRawAct.triggered.connect(lambda: self.writeVoltageCsv())

		startAct = QAction(QIcon('document.png'), 'Start', self)
		startAct.triggered.connect(lambda: self.startAll())

		
		self.toolbar = self.addToolBar('Exit')
		self.toolbar = self.addToolBar('Save')
		self.toolbar = self.addToolBar('Export')
		self.toolbar = self.addToolBar('Export')

		self.toolbar.addAction(exitAct)
		self.toolbar.addAction(startAct)
		self.toolbar.addAction(exportRawAct)
		self.toolbar.addAction(exportAct)

		print("Creating toolbar menus and displaying window")
		#Setting window size and showing
  
		self.show()

	def Close(self):
		p.stop()
		GPIO.cleanup()
		sys.exit()

	def analyzeHR(self, run=True):
		
		HR_ADCchan = 1

		run = True 

		all_data = []
		all_hr = []

		while run: 

			Value = []
			HR = []

			for i in range(10):
				hr_level = ReadChannel(HR_ADCchan)
				hr_value = ConvertVolts(hr_level, 2)
				hr = ConvertTemp(hr_level, 2)

				Value.append(hr_value)
				HR.append(hr)

			all_data.append(HR)
			HR_Wave = WaveletTransform(HR)
			peakind = signal.find_peaks_cwt(HR_wave, np.arange(1,1000))

			dist = []


			for i in range(length(peakind - 2)):

				dist.append(peakind[i+1] - peakind[i])

			heart_rate = np.mean(1./dist) 
			all_hr.append(heart_rate)
			lcd_HR.display(heart_rate)


		self.volt_hr = all_data
		self.real_hr = all_hr



	def analyzeBR(self, run=True):

		BR_ADCchan = 2

		all_data = []
		all_br = []

		run = True 

		while run: 

			Value = []
			BR = []

			for i in range(10):
				br_level = ReadChannel(BR_ADCchan)
				br_value = ConvertVolts(br_level, 2)
				br = ConvertTemp(hr_level, 2)

				Value.append(br_value)
				BR.append(br)

			all_data.append(BR)
			BR_Wave = WaveletTransform(BR)
			peakind = signal.find_peaks_cwt(BR_wave, np.arange(1,1000))

			dist = []

			for i in range(length(peakind - 2)):

				dist.append(peakind[i+1] - peakind[i])

			breath_rate = np.mean(1./dist) 
			all_br.append(breath_rate)
			lcd_BR.display(breath_rate)

		self.volt_br = all_data
		self.real_br = all_br


	def analyzeTEMP(self, run=True):

		Temp_ADCchan = 3
		all_data = []
		all_temp = []

		while run: 

			temp_level = ReadChannel(Temp_ADCchan)
			temp_value = ConvertVolts(temp_level, 2)
			temp = ConvertTemp(temp_level, 2)

			all_temp.append(temp)
			all_data.append(temp_value)

			lcd_BR.display(temp)

			time.sleep(5)

		self.volt_temp = all_data
		self.real_temp = all_temp

	def tempControl(self):

		self.p.start(100)

		while True:

			current_value = ConvertTemp(ConvertVolts(ReadChannel(2), 2), 2)
			print(current_value)

			newvalue = self.control.update(current_value=current_value)
			print(newvalue)

			if newvalue > current_value:

				direction = 0


			else: 

				direction = 4095


			dac.set_voltage(direction)
			
			time.sleep(2)


		
	def startAll(self):

		self.tempControl()
		self.displayVitals()
		self.lbl.plot()



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

	def displayVitals():

		while True:

			#read channels to display vitals 

			lcd_HR.display(np.mean(lbl.real_hr))
			lcd_BR.display(np.mean(lbl.real_br))
			lcd_TEMP.display(np.mean(lbl.real_temp))

	# IN PROGRESS - last line of loadCSV needs to be changed and graphs need to be made self variables upon initialization for dynamic changing and one for models for each vital

	def writeVoltageCsv(self, fileName):

		cwd = os.getcwd()

		volt_hr = self.lbl.volt_hr
		volt_br = self.lbl.volt_br
		volt_temp = self.lbl.volt_temp

		fileName_volt = cwd + fileName + "Voltage_Data.csv"
		

		data = pd.DataFrame({'Heart Rate (V)':volt_hr, 'Breathing Rate (V)':volt_br, 'Temperature (V)':volt_temp})
		data.to_csv(fileName_volt, index=False)

	def writeRealCsv(self, fileName):

		real_hr = self.lbl.real_hr
		real_br = self.lbl.real_br
		real_temp = self.lbl.real_temp

		fileName_real = cwd + fileName + "Vital_Data.csv"

		data = pd.DataFrame({'Heart Rate (bpm)':real_hr, 'Breathing Rate (bpm)':real_temp, 'Temperature (F)':real_temp})
		data.to_csv(fileName_real, index=False)



# TODO - Implement these methods 

class PlotCanvas(FigureCanvas):

	def __init__(self, parent=None, width=5, height=4, dpi=100, title=None, color='r-'):

		plt.ion()
		#self.data = genfromtxt('example-data.csv', dtype=None, delimiter=',')
		self.fig = Figure(figsize=(width, height), dpi=dpi)
		self.color = color 
		self.title = title
		self.current_time = 0
		self.window = 50

		self.HR = self.fig.add_subplot(311)
		self.BR = self.fig.add_subplot(312)
		self.Temp = self.fig.add_subplot(313)

		self.hr_y = deque([0.0]*self.window)
		self.br_y = deque([0.0]*self.window)
		self.temp_y = deque([0.0]*self.window)
		self.x = deque([0.0]*self.window)

		self.start = 0
 
		FigureCanvas.__init__(self, self.fig)
		self.setParent(parent)
 
		FigureCanvas.setSizePolicy(self,
				QtWidgets.QSizePolicy.Expanding,
				QtWidgets.QSizePolicy.Expanding)
		FigureCanvas.updateGeometry(self)
		self.fig.tight_layout(pad=1, w_pad=0.1, h_pad=0.1)

		print("Initializing PlotCanvas")

	def addToBuf(self, buf, val):

		if len(buf) < self.window:
			buf.append(val)
		else:
			buf.pop()
			buf.appendleft(val)

  # add data
	def add(self, buf, chan, time_check = False):
		
		if time_check == False: 
		
			self.addToBuf(buf, ConvertVolts(ReadChannel(chan), places=2))
			

		else:
			self.addToBuf(buf, (time.time()-self.start))


	def plot(self, window=50, start=0):


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

		self.start = time.time()

		line_hr, = self.HR.plot(self.x ,self.hr_y, '-g')
		line_br, = self.BR.plot(self.x ,self.br_y,  '-c')
		line_temp, = self.Temp.plot(self.x, self.temp_y, '-r')

		self.fig.canvas.draw_idle()
		self.fig.canvas.flush_events()

		plt.pause(0.05)

	
		while True:

			self.add(self.x, 0, time_check = True)
			self.add(self.hr_y, 0)
			self.add(self.br_y, 1)
			self.add(self.temp_y, 2)

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
			plt.pause(0.005)
			self.current_time = time.time()

		plt.show()




class PID:
	"""
	Discrete PID control
	"""

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

	def setIntegrator(self, Integrator):
		self.Integrator = Integrator

	def setDerivator(self, Derivator):
		self.Derivator = Derivator

	def setKp(self,P):
		self.Kp=P

	def setKi(self,I):
		self.Ki=I

	def setKd(self,D):
		self.Kd=D

	def getPoint(self):
		return self.set_point

	def getError(self):
		return self.error

	def getIntegrator(self):
		return self.Integrator

	def getDerivator(self):
		return self.Derivator
	
		
		
if __name__ == '__main__':
	
	app = QApplication(sys.argv)
	ex = MainWindow()
	sys.exit(app.exec_())

