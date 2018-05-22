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
import subprocess as sub 
import datetime 
from datetime import datetime as dt
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

GPIO.setup(33, GPIO.OUT)
GPIO.setup(29, GPIO.OUT)

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

	offset = 1/3300 
	volts = (data / 4096);  

	#print("Method Info")
	#print(volts)
	resistance = -10000*((5.0/volts)-1)  
	#print(resistance) 
	inverse = (1/20) + offset*np.log((resistance/10000))



	temp = 1/inverse 
	temp = round(temp, places)
	#print(temp)
	return temp 

def WaveletTransform(data):
	widths = np.arange(1,1000)
	cA = signal.cwt(data, signal.ricker, widths)
	return np.mean(cA, axis = 0)

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


		self.control = PID()
		self.control.setPoint(set_point=37)

		print("Initializing MainWindow")

		if not os.path.isdir('/home/pi/Documents/MouseVitalMonitoring/Voltage Data'):
			os.mkdir('/home/pi/Documents/MouseVitalMonitoring/Voltage Data')

		if not os.path.isdir('/home/pi/Documents/MouseVitalMonitoring/Vital Data'):
			os.mkdir('/home/pi/Documents/MouseVitalMonitoring/Vital Data')


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
		startAct.triggered.connect(lambda: self.lbl.plot(lcd_HR=self.lcd_HR, lcd_BR=self.lcd_BR, lcd_TEMP=self.lcd_TEMP, control=self.control))

		heatAct = QAction(QIcon('temperature icon.png'), 'Start Temperature', self)
		heatAct.triggered.connect(lambda: self.tempControl())

		vitalsAct = QAction(QIcon('vitals icon.png'), 'Start Recording', self)
		vitalsAct.triggered.connect(lambda: self.startVitals())



		
		self.toolbar = self.addToolBar('Exit')
		self.toolbar = self.addToolBar('Save')
		self.toolbar = self.addToolBar('Export')
		self.toolbar = self.addToolBar('Export')

		self.toolbar.addAction(exitAct)
		self.toolbar.addAction(startAct)
		self.toolbar.addAction(heatAct)
		self.toolbar.addAction(vitalsAct)
		self.toolbar.addAction(exportRawAct)
		self.toolbar.addAction(exportAct)

		print("Creating toolbar menus and displaying window")
		#Setting window size and showing
  
		self.show()

	def Close(self):



		
		sub.call(["git", "add", "."])
		sub.call(["git", "commit", "-m"])
		sub.call(["git", "push"])

		sys.exit()



	def tempControl(self):

		while True:

			current_value = ConvertTemp(ReadChannel(2), 1)

			#print(ReadChannel(2))
			print(current_value)

			newvalue = self.control.update(current_value=current_value)
			print(newvalue)

			if newvalue > current_value:

				direction = 1


			else: 

				direction = 0


			GPIO.output(33, 1)
			GPIO.output(29, direction)
			
			time.sleep(2)

		
	def startVitals(self):

		#self.tempControl()
		self.lbl.plot(lcd_HR=self.lcd_HR, lcd_BR=self.lcd_BR, lcd_TEMP=self.lcd_TEMP, control=self.control)
		

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

		today = dt.now()

		today = today.strftime("%Y-%m-%d %H:%M:%S")

		workingdir = os.getcwd() + '/Voltage Data/'

		time = self.lbl.x
		volt_hr = self.lbl.hr_volt
		volt_br = self.lbl.br_volt
		volt_temp = self.lbl.temp_volt

		len_x = len(time)
		len_hr = len(volt_hr)
		len_br = len(volt_br)
		len_temp = len(volt_temp)

		lengths = [len_hr; len_br; len_temp]

		x = min(int(s) for s in lengths)

		time = time[0:(x-1)]
		volt_hr = volt_hr[0:(x-1)]
		volt_br = volt_br[0:(x-1)]
		volt_temp = volt_temp[0:(x-1)]


		fileName_volt = workingdir  + 'Voltage_Data' + today + '.csv'
		

		data = pd.DataFrame({'Time (s)':time, 'Heart Rate (V)':volt_hr, 'Breathing Rate (V)':volt_br, 'Temperature (V)':volt_temp})
		data.to_csv(fileName_volt, index=False)

	def writeRealCsv(self):

		today = dt.now()

		today = today.strftime("%Y-%m-%d %H:%M:%S")

		workingdir = os.getcwd() + '/Vital Data/'

		time = self.lbl.x
		real_hr = self.lbl.hr_data
		real_br = self.lbl.br_data
		real_temp = self.lbl.temp_data

		len_x = len(time)
		len_hr = len(real_hr)
		len_br = len(real_br)
		len_temp = len(real_temp)

		lengths = [len_hr; len_br; len_temp]

		x = min(int(s) for s in lengths)

		time = time[0:(x-1)]
		real_hr = real_hr[0:(x-1)]
		real_br = real_br[0:(x-1)]
		real_temp = real_temp[0:(x-1)]


		fileName_real = workingdir  + 'Vital_Data' + today +  '.csv'

		data = pd.DataFrame({'Time (s)':time, 'Heart Rate (bpm)':real_hr, 'Breathing Rate (bpm)':real_temp, 'Temperature (F)':real_temp})
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
		self.window = 10000

		self.HR = self.fig.add_subplot(311)
		self.BR = self.fig.add_subplot(312)
		self.Temp = self.fig.add_subplot(313)

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

	

	def analyzeHR(self):

		Value = []
		HR = []

		peakind = signal.find_peaks(self.hr_y, distance = 2)

		dist = []


		for i in range(len(peakind) - 2):

			dist.append(peakind[i+1] - peakind[i])

		heart_rate = np.mean(1./np.array(dist)) 
		self.hr_data.append(heart_rate)
		return heart_rate


	def analyzeBR(self):


		Value = []
		BR = []

		peakind = signal.find_peaks(self.br_y, distance = 2)

		dist = []
		for i in range(len(peakind) - 2):

			dist.append(peakind[i+1] - peakind[i])

		breath_rate = np.mean(1./np.array(dist))
		self.br_data.append(breath_rate)
		return breath_rate


	def plot(self, lcd_HR, lcd_BR, lcd_TEMP, control, window=50, start=0):

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


			lcd_TEMP.display(ConvertTemp(ReadChannel(2), 2))
			lcd_HR.display(self.analyzeHR())
			lcd_BR.display(self.analyzeBR())


			if (self.analyzeBR() > 80 or self.analyzeBR() < 50):

				lcd_BR.setSegmentStyle(QLCDNumber.Filled)


			if (ConvertTemp(ReadChannel(2), 2) > 40 or ConvertTemp(ReadChannel(2), 2) < 35):

				lcd_TEMP.setSegmentStyle(QLCDNumber.Filled)

			for i in range(500):

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
			#plt.pause(0.00005)

			plt.show()


			current_value = ConvertTemp(ReadChannel(2), 1)

			#print(ReadChannel(2))
			print(current_value)

			newvalue = control.update(current_value=current_value)
			print(newvalue)

			if newvalue > current_value:

				direction = 1


			else: 

				direction = 0


			GPIO.output(33, 1)
			GPIO.output(29, direction)
			

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

