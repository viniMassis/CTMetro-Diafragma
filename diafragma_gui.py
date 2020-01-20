#TODO: Comunicação clp
#TODO: visualização dados

#!/usr/bin/env python
# -*- coding: utf-8 -*-0
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import pyqtgraph as pg
from pyqtgraph import PlotWidget, plot
import numpy as np

import sys
import Diafragma

class Window(QWidget):
    def __init__(self, parent=None):
        super(Window, self).__init__()
        self.setWindowTitle("test")
        
        self.tempo = []
        self.lvolume = []
        self.video = VideoThread()
        self.graphWidget = pg.PlotWidget()
        #self.setCentralWidget(self.graphWidget)
        #self.grafico()
        
        self.button1 = QPushButton(self)
        self.button1.setText("Inicio")
        self.button1.move(150,0)
        
        self.button2 = QPushButton(self)
        self.button2.setText("Captura")
        
        self.button3 = QPushButton(self)
        self.button3.setText("para")
        self.button3.move(0,150)
       
        self.button1.clicked.connect(self.inicia)
        self.button2.clicked.connect(self.roi)
        self.button3.clicked.connect(self.para)  

        self.conexaotimer = QTimer(self)
        self.conexaotimer.timeout.connect(self.volume)       
        
    def roi(self):
        self.video.roi()
    def inicia(self):
        self.video.start()
        self.conexaotimer.start(1*1000) 
        self.graphWidget.show()
    def volume(self):
        if len(self.tempo)>0:
            self.tempo.append(self.tempo[-1]+1)
        else:
            self.tempo.append(1)
        self.lvolume.append(self.video.d.volume)
        self.graphWidget.plot(self.tempo, self.lvolume)  
    def para(self):
        self.conexaotimer.stop()
        self.tempo = []
        self.lvolume = []
        self.graphWidget.plot(self.tempo, self.lvolume)
        
        
class VideoThread(QThread):
    frame = pyqtSignal(object)
    def __init__(self):
        QThread.__init__(self)
        #self.d = 0
    def __del__(self):
        self.wait()
    def roi(self):
        self.d = Diafragma.Diafragma("teste", 'C://Users//viniciusassis//Documents//GitHub//visaoMaquina//videos//diafragma.webm')
        self.d.regiao()
    def run(self):
        self.d.run(100)
        

class GraficosThread():
    def __init__(self):
        QThread.__init__(self)
    def run(self):
        pass
        
        
root = QApplication(sys.argv)
app = Window()
app.show()
sys.exit(root.exec_())