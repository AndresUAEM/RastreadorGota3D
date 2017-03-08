# -*- coding: utf-8 -*-
import sys
import os
import threading
import time
os.environ['ETS_TOOLKIT'] = 'qt4'
#os.environ['QT_API'] = 'pyqt'
from pyface.qt import QtGui, QtCore
from Animacion import Animacion
from OpenWindow import OpenWindow
from tkFileDialog import asksaveasfilename, askopenfilename
from Tkinter import Tk
from py4j.java_gateway import JavaGateway
from Tracker import Tracks
################################################################################


class Principal(QtGui.QMainWindow):
    
    def desbloquear(self):            
        self.botonPlay.setEnabled(True)
        self.sliderFrame.setEnabled(True)
        self.sliderFrame.setMaximum(self.tracks.duracion-1)
        self.cambiarFrame()
        self.botonGuardarTrayectorias.setEnabled(True)
        self.botonGuardarVideo.setEnabled(True)
        for cb in self.checkBoxParticulas:
            cb.setEnabled(True)
        self.accionCheckBox()
        
    def abrir(self):
        self.aplicacionAbrir=OpenWindow(self)
        tracks=[]
        try:
            self.tracks=self.aplicacionAbrir.tracks
            print('Trayectorias cargadas')
        except AttributeError:
            print 'Inicie máquina virtual (JVM)'
            sys.exit()
        self.animacion.actualizar(self.tracks)
        self.desbloquear()
        
    
    def cargar(self):
        Tk().withdraw()
        nombre=askopenfilename()
        print(nombre)
        gateway = JavaGateway()
        datos=gateway.entry_point.cargarXML(nombre)
        self.tracks=Tracks(datos)
        self.tracks.guardar('Archivo.csv')
        self.animacion.actualizar(self.tracks)
        self.desbloquear()
        
    def guardar(self):
        Tk().withdraw()
        archivo=asksaveasfilename()
        self.tracks.guardar(archivo.name+'.csv')
        
    def guardarVideo(self):
        Tk().withdraw()
        archivo=asksaveasfilename()
        self.animacion.guardarVideo(archivo)
            
    def crearMenu(self):
        self.menubar=QtGui.QMenuBar()
        self.menuArchivo = self.menubar.addMenu('&Archivo')
        self.botonAbrir  = self.menuArchivo.addAction('&Abrir',self.abrir)
        self.botonAbrir  = self.menuArchivo.addAction('&Cargar XML',self.cargar)
        self.botonGuardarTrayectorias= self.menuArchivo.addAction('&Guardar Trayectorias',self.guardar)
        self.botonGuardarTrayectorias.setEnabled(False)
        self.botonGuardarVideo= self.menuArchivo.addAction('&Guardar Video',self.guardarVideo)
        self.botonGuardarVideo.setEnabled(False)
        
        self.menuEditar = self.menubar.addMenu('&Editar')
        self.layout.addWidget(self.menubar)
    
    def cambiarFrame(self):
        self.animacion.mayavi_widget.visualization.cambiarFrame(self.sliderFrame.value())
        self.labelIndice.setText(str(self.sliderFrame.value())+'/'+str(self.tracks.duracion-1))
    
    def play(self,val,val2):
        while self.continuarReproduccion:
            print(self.indice)
            self.indice=(self.indice+1)%(self.tracks.duracion-1)
            self.sliderFrame.setValue(self.indice)
            time.sleep(0.125)
        self.continuarReproduccion=True
    
    def reproducir(self):
        try:
            if self.t1.isAlive():
                self.continuarReproduccion=False
            else:
                self.t1.start()                
        except RuntimeError:
            self.t1 = threading.Thread(target=self.play, args=(0,0))
            self.t1.start()          
    
    def accionCheckBox(self):
        self.animacion.cambiarVisibilidad([cb.isChecked() for cb in self.checkBoxParticulas])
    
    def crearCheckBoxes(self):
        self.checkBoxParticulas=[]
        self.checkBoxParticulas.append(QtGui.QCheckBox('Hacia centro (Rojo)'))
        self.checkBoxParticulas.append(QtGui.QCheckBox('Hacia fuera (Verde)'))
        #self.checkBoxParticulas.append(QtGui.QCheckBox('Hacia arriba (Rojo)'))
        #self.checkBoxParticulas.append(QtGui.QCheckBox('Hacia abajo (Blanco)'))
        layout=QtGui.QHBoxLayout()
        for cb in self.checkBoxParticulas:
            cb.setEnabled(False)
            cb.stateChanged.connect(self.accionCheckBox)
            layout.addWidget(cb)
        self.layout.addLayout(layout)
        
    def crearLayout(self):
        self.layout = QtGui.QVBoxLayout()
        self.crearMenu()
        self.container.setLayout(self.layout)
        self.animacion = Animacion()
    
        self.layout.addWidget(self.animacion.mayavi_widget)
        self.botonPlay = QtGui.QToolButton()
        self.botonPlay.setText(">")
        self.botonPlay.setEnabled(False)
        self.botonPlay.clicked.connect(self.reproducir)
        self.sliderFrame=QtGui.QSlider(QtCore.Qt.Horizontal)
        self.sliderFrame.valueChanged.connect(self.cambiarFrame)
        self.sliderFrame.setEnabled(False)
        self.labelIndice=QtGui.QLabel('0/0')
        self.crearCheckBoxes()
        layout2 = QtGui.QHBoxLayout()
        layout2.addWidget(self.botonPlay)
        layout2.addWidget(self.sliderFrame)
        layout2.addWidget(self.labelIndice)
        self.layout.addLayout(layout2)
        
        
    def __init__(self):
        super(Principal, self).__init__(None)
    
        self.container = QtGui.QWidget()
        self.container.setWindowTitle("Rastreador")
        self.crearLayout()        
        self.setWindowModality(QtCore.Qt.WindowModal)
        self.container.show()
        self.setCentralWidget(self.container)
        self.show()
        self.t1 = threading.Thread(target=self.play, args=(0,0))
        self.continuarReproduccion=True
        self.indice=0

if __name__ == "__main__":
    app = QtGui.QApplication.instance()
    p=Principal()
    #app.exec_()
    #sys.exit(app.exec_())
    print 1+1
