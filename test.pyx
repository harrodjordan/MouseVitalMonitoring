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
		self.data_hr = genfromtxt('breathdata.csv', dtype=None, delimiter=',')
		self.data_br = genfromtxt('heartdata.csv', dtype=None, delimiter=',')
		self.data_temp = genfromtxt('faketemp2.csv', dtype=None, delimiter=',')
		self.data = genfromtxt('timedata.csv', dtype=None, delimiter=',')
		print(self.data.shape)
		print(self.data_hr.shape)

		self.fig = Figure(figsize=(width, height), dpi=dpi)
		self.color = color 
		self.title = title
		self.current_time = 0
		self.window = 50

		self.HR = self.fig.add_subplot(311)
		self.BR = self.fig.add_subplot(312)
		self.Temp = self.fig.add_subplot(313)

		self.volt_hr = None
		self.real_hr = None

		self.volt_br = None
		self.real_br = None

		self.volt_temp = None
		self.real_temp = None

 
		FigureCanvas.__init__(self, self.fig)
		self.setParent(parent)
 
		FigureCanvas.setSizePolicy(self,
				QtWidgets.QSizePolicy.Expanding,
				QtWidgets.QSizePolicy.Expanding)
		FigureCanvas.updateGeometry(self)
		self.fig.tight_layout(pad=1, w_pad=0.1, h_pad=0.1)
		#self.plot()
 
	def analyzeHR(self, run=True):

		self.data_hr = genfromtxt('breathdata.csv', dtype=None, delimiter=',')
		
		HR_ADCchan = 1

		run = True 

		all_data = []
		all_hr = []

		count = 0

		while run: 

			Value = []
			HR = []

			HR_Wave = WaveletTransform(self.data[1+count:5000+count, 1])
			peakind = signal.find_peaks_cwt(HR_wave, np.arange(1,1000))

			dist = []


			for i in range(length(peakind - 2)):

				dist.append(peakind[i+1] - peakind[i])

			heart_rate = np.mean(1./dist)
			self.lcd_HR.display(heart_rate)
			all_hr.append(heart_rate)

			count = count + 10
			print(count)


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
			peakind = BR_Wave #signal.find_peaks_cwt(BR_wave, np.arange(1,1000))

			dist = []

			for i in range(length(peakind - 2)):

				dist.append(peakind[i+1] - peakind[i])

			breath_rate = np.mean(1./dist) 
			print(breath_rate)
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


	def plot1(self, data):
		ax = self.figure.add_subplot(111)
		ax.plot(data, self.color)
		ax.set_title(self.title)
		xtext = ax.set_xlabel('Time (s)') # returns a Text instance
		ytext = ax.set_ylabel('Volts (mV)')
		ax.autoscale(enable=True, axis='x', tight=True)

		[m, n] = np.size(data)

		for i in range(n):
			ax.plot(data[1:i,:], self.color)
			plt.draw()
			plt.pause(0.05)

		while True:
			plt.pause(0.05)
			self.draw()



	def plot(self, window=50, start=0, lcd_HR, lcd_BR, lcd_TEMP):


		self.window = window 
		self.HR.set_title('Heart Rate')
		self.BR.set_title('Breathing Rate')
		self.Temp.set_title('Current Temperature')

		xtext_hr = self.HR.set_xlabel('Time (s)') # returns a Text instance
		ytext_hr = self.HR.set_ylabel('Volts (V)')

		xtext_br = self.BR.set_xlabel('Time (s)') # returns a Text instance
		ytext_br = self.BR.set_ylabel('Volts (V)')

		xtext_temp = self.Temp.set_xlabel('Time (s)') # returns a Text instance
		ytext_temp = self.Temp.set_ylabel('Temperature (C)')

		line_hr, = self.HR.plot(self.data[1:self.window] ,self.data_hr[1:self.window], '-g')
		line_br, = self.BR.plot(self.data[1:self.window] ,self.data_br[1:self.window], '-c')
		line_temp, = self.Temp.plot(self.data[1:self.window] ,self.data_temp[1:self.window], '-r')

		self.fig.canvas.draw_idle()
		self.fig.canvas.flush_events()

		plt.pause(0.05)

	
		for i in range(len(self.data)):
			self.HR.set_ylim(min(self.data_hr[i:self.window+i]), max(self.data_hr[i:self.window+i]))
			self.HR.set_xlim(min(self.data[i:self.window+i]), max(self.data[i:self.window+i]))
			line_hr.set_data(self.data[i:self.window+i], self.data_hr[i:self.window+i])

			self.BR.set_ylim(min(self.data_br[i:self.window+i]), max(self.data_br[i:self.window+i]))
			self.BR.set_xlim(min(self.data[i:self.window+i]), max(self.data[i:self.window+i]))
			line_br.set_data(self.data[i:self.window+i], self.data_br[i:self.window+i])

			self.Temp.set_ylim(min(self.data_temp[i:self.window+i]), max(self.data_temp[i:self.window+i]))
			self.Temp.set_xlim(min(self.data[i:self.window+i]), max(self.data[i:self.window+i]))
			line_temp.set_data(self.data[i:self.window+i], self.data_temp[i:self.window+i])


			self.fig.canvas.draw_idle()
			

			self.fig.canvas.flush_events()
			plt.show()
			plt.pause(0.05)
			self.current_time = i

		plt.show()





	
		
		
if __name__ == '__main__':
	
	app = QApplication(sys.argv)
	ex = MainWindow()
	sys.exit(app.exec_())