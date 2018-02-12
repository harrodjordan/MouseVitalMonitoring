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
#import PIL.Image
import os, os.path
import random
import argparse
import sys
import csv

import tkinter


class MainWindow(QMainWindow):

	def __init__(self):

		super().__init__()

		self.initUI()


	def initUI(self):  

		lcd = QLCDNumber(self)
		label = QLabel('Breathing Rate (breaths/min)')

		breathing = QPixmap("breathing.png")

		lbl2 = QLabel(self)
		lbl2.setPixmap(breathing)

		HR = QPixmap("hr.png")

		lbl3 = QLabel(self)
		lbl3.setPixmap(HR)

		wid = QWidget(self)
		self.setCentralWidget(wid)

		box = QHBoxLayout(self)

		tlbox = QHBoxLayout(self)

		tlbox.addWidget(label, alignment=(Qt.AlignTop | Qt.AlignLeft))

		tlbox.addWidget(lcd)
	
		
		

		# add label for breathing rate 

		topleft = QFrame(self)
		topleft.setFrameShape(QFrame.StyledPanel)

		topleft.setLayout(tlbox)

		trbox = QHBoxLayout(self)
		trbox.addWidget(lbl2)

		# add fake graph for breathing curve
 
		topright = QFrame(self)
		topright.setFrameShape(QFrame.StyledPanel)

		topright.setLayout(trbox)

		bbox = QHBoxLayout(self)
		bbox.addWidget(lbl3)

		bottom = QFrame(self)
		bottom.setFrameShape(QFrame.StyledPanel)

		# add fake hr data 

		bottom.setLayout(bbox)

		splitter1 = QSplitter(Qt.Horizontal)
		splitter1.addWidget(topleft)
		splitter1.addWidget(topright)

		splitter2 = QSplitter(Qt.Vertical)
		splitter2.addWidget(splitter1)
		splitter2.addWidget(bottom)

		box.addWidget(splitter2)
		wid.setLayout(box)       
	
		menubar = self.menuBar()
		fileMenu = menubar.addMenu('File')
		viewMenu = menubar.addMenu('View')

		self.statusbar = self.statusBar()
		self.statusbar.showMessage('Ready')
	
		impMenu = QMenu('Import', self)
		impAct = QAction('Import data', self) 
		impMenu.addAction(impAct)

		expMenu = QMenu('Export', self)
		expAct = QAction('Export data', self) 
		expMenu.addAction(expAct)
		
		
		newAct = QAction('New', self)        
		
		fileMenu.addAction(newAct)
		fileMenu.addMenu(impMenu)
		fileMenu.addMenu(expMenu)

		viewStatAct = QAction('View statusbar', self, checkable=True)
		viewStatAct.setStatusTip('View statusbar')
		viewStatAct.setChecked(True)
		viewStatAct.triggered.connect(self.toggleMenu)
		viewMenu.addAction(viewStatAct)

		exitAct = QAction(QIcon('exit24.png'), 'Exit', self)
		exitAct.setShortcut('Ctrl+Q')
		exitAct.triggered.connect(qApp.quit)
		
		self.toolbar = self.addToolBar('Exit')
		self.toolbar.addAction(exitAct)


   
		
		
		self.setGeometry(200, 200, 1200, 1200)
		self.setWindowTitle('Rodent Vitals Monitoring System')    
		self.show()


	
	def toggleMenu(self, state):
		
		if state:
			self.statusbar.show()
		else:
			self.statusbar.hide()

	
		
		
if __name__ == '__main__':
	
	app = QApplication(sys.argv)
	ex = MainWindow()
	sys.exit(app.exec_())



# if __name__ == "__main__":
# 	app = QApplication(sys.argv)
# 	squiggly = MainWindow()
# 	squiggly.show();
# 	app.exec_()
