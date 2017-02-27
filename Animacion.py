import sys
import os
import shutil
os.environ['ETS_TOOLKIT'] = 'qt4'
#os.environ['QT_API'] = 'pyqt'
from pyface.qt import QtGui, QtCore

from traits.api import HasTraits, Instance, on_trait_change
from traitsui.api import View, Item
from mayavi.core.ui.api import MayaviScene, MlabSceneModel,SceneEditor

#The actual visualization
class Visualization(HasTraits):
    scene = Instance(MlabSceneModel, ())
        
    def cambiarFrame(self,t):
        self.flechas.mlab_source.set(x=self.vectX[t], y=self.vectY[t], z=self.vectZ[t], u=self.vectU[t], v=self.vectV[t], w=self.vectW[t])
        self.esferas.mlab_source.reset(x=self.x[t],y=self.y[t],z=self.z[t])
    
    def guardarImagen(self,nombre):
        self.scene.save(nombre+'.png')
        
    def crearPuntos(self,tracks,lmin):
        x=[]
        y=[]
        z=[]
        for tiempo in range(self.tmax):
            #Obtener puntos
            x1,y1,z1=tracks.puntos(tiempo,lmin)
            x.append(x1)
            y.append(y1)
            z.append(z1)
        return  x,y,z
        
    def crearVectores(self,tracks,lmin):
        vectX=[]
        vectY=[]
        vectZ=[]
        vectU=[]
        vectV=[]
        vectW=[]
        self.vectX2=[]
        self.vectY2=[]
        self.vectZ2=[]
        self.vectU2=[]
        self.vectV2=[]
        self.vectW2=[]
        tama=0
        for tiempo in range(self.tmax):
            #Obtener self.vectores
            x2,y2,z2,u,v,w=tracks.vectores(tiempo,lmin)
            vectX.append(x2)
            vectY.append(y2)
            vectZ.append(z2)
            vectU.append(u)
            vectV.append(v)
            vectW.append(w)
            for i in range(len(x2)):
                self.vectX2.append(x2[i])
                self.vectY2.append(y2[i])
                self.vectZ2.append(z2[i])
                self.vectU2.append(u[i])
                self.vectV2.append(v[i])
                self.vectW2.append(w[i])
            if len(x2)>tama:
                tama=len(x2)
        for tiempo in range(self.tmax):
            i=len(vectX[tiempo])
            while (len(vectX[tiempo])<tama):
                vectX[tiempo].append(vectX[tiempo][0])
                vectY[tiempo].append(vectY[tiempo][0])
                vectZ[tiempo].append(vectZ[tiempo][0])
                vectU[tiempo].append(vectU[tiempo][0])
                vectV[tiempo].append(vectV[tiempo][0])
                vectW[tiempo].append(vectW[tiempo][0])
        return vectX,vectY,vectZ,vectU,vectV,vectW
    
    def separarPorSentido(self,centro):
        self.haciaDentro=[]
        self.haciaFuera=[]
    
    def mostrar(self,tracks,lmin=0):
        self.tmax=tracks.duracion
        self.x,self.y,self.z = self.crearPuntos(tracks,lmin)
        self.vectX,self.vectY,self.vectZ,self.vectU,self.vectV,self.vectW = self.crearVectores(tracks,lmin)
        self.centroX=(tracks.xMax+tracks.xMin)/2
        self.centroY=(tracks.yMax+tracks.yMin)/2
        i=0
        
        #self.flechas2=self.scene.mlab.quiver3d(self.vectX2, self.vectY2, self.vectZ2, self.vectU2, self.vectV2, self.vectW2,color=(0,0,0),opacity=0.1)
        self.flechas=self.scene.mlab.quiver3d(self.vectX[i], self.vectY[i], self.vectZ[i], self.vectU[i], self.vectV[i], self.vectW[i],color=(0,0,1))
        self.esferas=self.scene.mlab.points3d(self.x[i],self.y[i],self.z[i],scale_factor=1)
        self.centro=self.scene.mlab.points3d([self.centroX],[self.centroY],[0],scale_factor=20)
        self.scene.mlab.outline()
        self.scene.mlab.axes()
        

    # the layout of the dialog screated
    view = View(Item('scene', editor=SceneEditor(scene_class=MayaviScene),
                     height=250, width=300, show_label=False),
                resizable=True)
    

    
################################################################################
# The QWidget containing the visualization, this is pure PyQt4 code.
class MayaviQWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        layout = QtGui.QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self.visualization = Visualization()
        # The edit_traits call will generate the widget to embed.
        self.ui = self.visualization.edit_traits(parent=self,kind='subpanel').control
        layout.addWidget(self.ui)
        self.ui.setParent(self)


class Animacion:
    def __init__(self):
        self.mayavi_widget = MayaviQWidget()
        
    def actualizar(self,tracks):
        vis=self.mayavi_widget.visualization.mostrar(tracks)
    
    def guardarVideo(self,nombre):
        vis=self.mayavi_widget.visualization
        cwd = os.getcwd()
        if os.path.exists(cwd+'/vid'):
            shutil.rmtree(cwd+'/vid')
        os.mkdir(cwd+'/vid')
        for t in range(len(vis.x)):
            self.mayavi_widget.visualization.cambiarFrame(t)
            vis.guardarImagen(cwd+'/vid/Frame'+str(t))