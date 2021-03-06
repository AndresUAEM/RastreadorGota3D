import sys
import os
import shutil
os.environ['ETS_TOOLKIT'] = 'qt4'
#os.environ['QT_API'] = 'pyqt'
from pyface.qt import QtGui, QtCore

from traits.api import HasTraits, Instance, on_trait_change
from traitsui.api import View, Item
from mayavi.core.ui.api import MayaviScene, MlabSceneModel,SceneEditor

class Vectores:
    def __init__(self):
        self.x=[]
        self.y=[]
        self.z=[]
        self.u=[]
        self.v=[]
        self.w=[]
        
    def  agregar(self,x,y,z,u,v,w):
        self.x.append(x)
        self.y.append(y)
        self.z.append(z)
        self.u.append(u)
        self.v.append(v)
        self.w.append(w)
    
    def rellenar(self):
        tama=0
        for tiempo in range(len(self.x)):
            #Obtener self.vectores
            if len(self.x[tiempo])>tama:
                tama=len(self.x[tiempo])
        for tiempo in range(len(self.x)):
            while (len(self.x[tiempo])<tama):
                self.x[tiempo].append(self.x[tiempo][0])
                self.y[tiempo].append(self.y[tiempo][0])
                self.z[tiempo].append(self.z[tiempo][0])
                self.u[tiempo].append(self.u[tiempo][0])
                self.v[tiempo].append(self.v[tiempo][0])
                self.w[tiempo].append(self.w[tiempo][0])
        
#The actual visualization
class Visualization(HasTraits):
    scene = Instance(MlabSceneModel, ())
    pCentro = (1,0,0)
    pFuera = (0,1,0)
    pCentroTrack=(1,1,0)
    pFueraTrack=(0,1,1)
    
    def cambiarFrame(self,i):
        #self.flechasVerdes.mlab_source.set(x=self.vectVerdes.x[i], y=self.vectVerdes.y[i], z=self.vectVerdes.z[i], u=self.vectVerdes.u[i], v=self.vectVerdes.v[i], w=self.vectVerdes.w[i],color=(0,1,0))
        #self.flechasRojas.mlab_source.set(x=self.vectRojos.x[i], y=self.vectRojos.y[i], z=self.vectRojos.z[i], u=self.vectRojos.u[i], v=self.vectRojos.v[i], w=self.vectRojos.w[i],color=(1,0,0))
        self.esferas[0].mlab_source.reset(x=self.x[0][i],y=self.y[0][i],z=self.z[0][i],scale_factor=1,color=self.pCentro)
        self.esferas[1].mlab_source.reset(x=self.x[1][i],y=self.y[1][i],z=self.z[1][i],scale_factor=1,color=self.pFuera)
        self.esferas2[0].mlab_source.reset(x=self.x2[0][i],y=self.y2[0][i],z=self.z2[0][i],scale_factor=1,color=self.pCentroTrack)
        self.esferas2[1].mlab_source.reset(x=self.x2[1][i],y=self.y2[1][i],z=self.z2[1][i],scale_factor=1,color=self.pFueraTrack)
        #self.esferas[2].mlab_source.reset(x=self.x[2][i],y=self.y[2][i],z=self.z[2][i],scale_factor=1,color=(1,0,0))
        #self.esferas[3].mlab_source.reset(x=self.x[3][i],y=self.y[3][i],z=self.z[3][i],scale_factor=1,color=(1,1,1))
    def guardarImagen(self,nombre):
        self.scene.save(nombre+'.png')
    
    def cambiarVisibilidad(self,lista):
        for i in range(len(self.esferas)):
            print(lista[i])
            if lista[i]:
                self.esferas[i].visible=True
            else:
                self.esferas[i].visible=False
    
    def crearPuntos(self,tracks,lmin):
        x=[[] for i in range(2)]
        y=[[] for i in range(2)]
        z=[[] for i in range(2)]
        sentidos=tracks.sentidos(self.centroX,self.centroY,lmin)
        for tiempo in range(self.tmax):
            #Obtener puntos
            x1,y1,z1=tracks.puntos(tiempo,lmin)
            x2=[[] for i in range(2)]
            y2=[[] for i in range(2)]
            z2=[[] for i in range(2)]
            for i in range(len(x1)):
                j=sentidos[tiempo][i]
                x2[j].append(x1[i])
                y2[j].append(y1[i])
                z2[j].append(z1[i])
            for i in range(2):
                x[i].append(x2[i])
                y[i].append(y2[i])
                z[i].append(z2[i])
        return  x,y,z
    
    def crearTrayectorias(self,tracks,lmin):
        vect=Vectores()
        for tiempo in range(self.tmax):
            x,y,z,u,v,w=tracks.vectores(tiempo,lmin)
            for i in range(len(x)):
                vect.x.append(x[i])
                vect.y.append(y[i])
                vect.z.append(z[i])
                vect.u.append(u[i])
                vect.v.append(v[i])
                vect.w.append(w[i])

        return vect
        
    def crearVectores(self,tracks,lmin):
        verdes=Vectores()
        rojos=Vectores()
        for tiempo in range(self.tmax):
            #Obtener self.vectores
            x1,y1,z1,u1,v1,w1,x2,y2,z2,u2,v2,w2=tracks.vectoresSeparados(self.centroX,self.centroY,tiempo,lmin)
            verdes.agregar(x1,y1,z1,u1,v1,w1)
            rojos.agregar(x2,y2,z2,u2,v2,w2)
        verdes.rellenar()
        rojos.rellenar()
        return verdes,rojos
    
    def mostrar(self,tracks,lmin=2):
        self.tmax=tracks.duracion
        lmin=self.tmax
        #self.centroX=(tracks.xMax+tracks.xMin)/2
        #self.centroY=(tracks.yMax+tracks.yMin)/2
        self.centroX=148
        self.centroY=206
        #self.sentidos=tracks.sentidos(self.centroX,self.centroY,3)
        self.x,self.y,self.z = self.crearPuntos(tracks,6*self.tmax/8)
        #self.vectVerdes,self.vectRojos = self.crearVectores(tracks,lmin)
        i=0
        self.completas=self.crearTrayectorias(tracks,self.tmax)
        #self.scene.mlab.bgcolor=(1,1,1)
        self.scene.mlab.figure(self.scene.mlab.gcf(),bgcolor=(0,0,0))
        self.trayectorias=self.scene.mlab.quiver3d(self.completas.x,self.completas.y,self.completas.z,self.completas.u,self.completas.v,self.completas.w,color=(0.7,0.7,0.7),opacity=0.7,scale_factor=1.0)
        
        
        self.esferas=[]
        self.esferas.append(self.scene.mlab.points3d(self.x[0][i],self.y[0][i],self.z[0][i],scale_factor=1,color=self.pCentro))
        self.esferas.append(self.scene.mlab.points3d(self.x[1][i],self.y[1][i],self.z[1][i],scale_factor=1,color=self.pFuera))
        self.scene.mlab.outline()
        self.x2,self.y2,self.z2 = self.crearPuntos(tracks,self.tmax)
        self.esferas2=[]
        self.esferas2.append(self.scene.mlab.points3d(self.x2[0][i],self.y2[0][i],self.z2[0][i],scale_factor=2,color=self.pCentroTrack))
        self.esferas2.append(self.scene.mlab.points3d(self.x2[1][i],self.y2[1][i],self.z2[1][i],scale_factor=2,color=self.pFueraTrack))
        #self.centro=self.scene.mlab.points3d([self.centroX],[self.centroY],[0],scale_factor=20)
        
        

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
    
    def cambiarVisibilidad(self,lista):
        self.mayavi_widget.visualization.cambiarVisibilidad(lista)
        
    def guardarVideo(self,nombre):
        vis=self.mayavi_widget.visualization
        cwd = os.getcwd()
        if os.path.exists(cwd+'/vid'):
            shutil.rmtree(cwd+'/vid')
        os.mkdir(cwd+'/vid')
        for t in range(vis.tmax):
            self.mayavi_widget.visualization.cambiarFrame(t)
            vis.guardarImagen(cwd+'/vid/Frame'+str(t))