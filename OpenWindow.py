# -*- coding: utf-8 -*-
import sys
from pyface.qt import QtGui,QtCore
from Tkinter import Tk
from tkFileDialog import askdirectory

from py4j.java_gateway import JavaGateway
from Tracker import Tracks

#from fiji import plugin

class OpenWindow(QtGui.QDialog):
    def explorar(self):
        Tk().withdraw()
        filename = askdirectory(initialdir=self.textboxFolder.text())
        self.textboxFolder.setText(filename)
        print(filename)
    
    def guardarParametros(self):
        archivo=open("Parametros.log",'w')
        archivo.write(self.textboxFolder.text()+'\t')
        archivo.write(self.textboxDiametro.text()+'\t')
        archivo.write(self.textboxThreshold.text()+'\t')
        archivo.write(self.textboxDistancia.text())


    def aceptar(self):
        print('ok')
        self.guardarParametros()
        gateway = JavaGateway()
        #print(gateway)
        gateway.entry_point.establecerParametros(self.textboxFolder.text(),float(self.textboxDiametro.text()),float(self.textboxThreshold.text()),float(self.textboxDistancia.text()))
        gateway.entry_point.abrir()
        gateway.entry_point.setVoxelSize()
        #gateway.entry_point.mostrar()
        datos=gateway.entry_point.localizar()
        self.tracks=Tracks(datos)
        #self.tracks.imprimir()
        self.tracks.guardar('Tracks.csv')
        self.close()
        #else:
        #    print 'Error en la maquina virtual (JVM)'
        
    def cargarParametros(self):
        try:
            archivo=open("Parametros.log",'r')
            datos=archivo.read().split('\t')
            
            self.textboxFolder.setText(datos[0])
            self.textboxDiametro.setText(datos[1])
            self.textboxThreshold.setText(datos[2])
            self.textboxDistancia.setText(datos[3])
        except:
            self.textboxDiametro.setText('3')
            self.textboxThreshold.setText('3')
            self.textboxDistancia.setText('20')

    def __init__(self,padre=None):
        #app = QtGui.QApplication.instance()
        super(OpenWindow, self).__init__(padre)
        
        
        self.ok=False
        self.textboxFolder    = QtGui.QLineEdit(readOnly=True)
        self.botonExplorar    = QtGui.QPushButton('Buscar')
        self.botonExplorar.clicked.connect(self.explorar)
        
        self.textboxDiametro  = QtGui.QLineEdit()
        self.textboxThreshold = QtGui.QLineEdit()
        self.textboxDistancia = QtGui.QLineEdit()
        self.botonAceptar = QtGui.QPushButton('OK')
        self.botonAceptar.clicked.connect(self.aceptar)
        
        self.cargarParametros()
        
        layout=QtGui.QGridLayout()
        
        #Arriba
        layout.addWidget(QtGui.QLabel('Direccion'), 0, 0)
        layout.addWidget(self.textboxFolder, 1, 0,columnSpan=3)
        layout.addWidget(self.botonExplorar, 1, 3)
        #Abajo izq
        layout.addWidget(QtGui.QLabel('Segmentacion'), 2, 0)
        layout.addWidget(QtGui.QLabel('Diametro estimado'), 3, 0)
        layout.addWidget(self.textboxDiametro, 3, 1)
        layout.addWidget(QtGui.QLabel('Umbral'), 4, 0)
        layout.addWidget(self.textboxThreshold, 4, 1)
        #Abajo der
        layout.addWidget(QtGui.QLabel('Rastreo'), 2, 2)
        layout.addWidget(QtGui.QLabel('Distancia maxima'), 3, 2)
        layout.addWidget(self.textboxDistancia, 3, 3)
        
        layout.addWidget(self.botonAceptar, 5, 3)
        self.setLayout(layout)
        self.setWindowTitle('Abrir')
        self.show()
        self.exec_()

if __name__ == "__main__":
    abrir=OpenWindow()
    print(1+1)