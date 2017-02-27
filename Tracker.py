# -*- coding: utf-8 -*-
import numpy as np
class Punto():
    """Almacena la posicion (x,y,z) en un tiempo t de una particula.
    """
    def __init__(self,x,y,z,t):
        self.x=x
        self.y=y
        self.z=z
        self.t=t

    def imprimir(self):
        print(int(self.t)+' ('+str(self.x)+','+str(self.y)+','+str(self.z)+')')

class Track():
    def __init__(self,nombre=''):
        self.puntos=[]
        self.nombre=nombre
    
    #Inserta una particula (x,y,z) en el tiempo t.
    def agregar(self,x,y,z,t):
        punto=Punto(x,y,z,t)
        if (len(self.puntos)==0) or (self.puntos[len(self.puntos)-1].t<t):
            self.puntos.append(punto)
        else:
            puntosAux=[]
            i=0
            while self.puntos[i].t<t:
                puntosAux.append(self.puntos[i])
                i+=1
            puntosAux.append(punto)
            while i<len(self.puntos):
                puntosAux.append(self.puntos[i])
                i+=1
            self.puntos=puntosAux
            
    def imprimir(self):
        #print
        print(self.nombre)
        #print(len(self.puntos))
        for p in self.puntos:
            p.imprimir()
            
    def posicion(self,tiempo):
        puntos=self.puntos
        if (puntos[len(puntos)-1].t >= tiempo):
            i=0
            while puntos[i].t < tiempo:
                i+=1
            if puntos[i].t==tiempo:
                return puntos[i].x,puntos[i].y,puntos[i].z
        return None,None,None
        
    def siguiente(self,tiempo):
        puntos=self.puntos
        if (puntos[len(puntos)-1].t >= tiempo+1):
            i=0
            while puntos[i].t < tiempo+1:
                i+=1
            if puntos[i].t==tiempo+1:
                return puntos[i].x,puntos[i].y,puntos[i].z
        return None,None,None
        
    def longitud(self):
        return len(self.puntos)
        
class Tracks():
    def __init__(self,datos):
        self.tracks=[]
        self.xMin=  np.inf
        self.xMax= -np.inf
        self.yMin=  np.inf
        self.yMax= -np.inf
        for trayectoria in datos:
            r=Track()
            for vals  in trayectoria:
                x=float(vals[0])
                y=float(vals[1])
                z=float(vals[2])
                t=int(vals[3])
                #print(t)
                r.agregar(x,y,z,t)
                
                if x<self.xMin:
                    self.xMin=x
                if x>self.xMax:
                    self.xMax=x
                if y<self.yMin:
                    self.yMin=y
                if y>self.yMax:
                    self.yMax=y                    
            self.tracks.append(r)
            self.duracion=max(track.puntos[len(track.puntos)-1].t for track in self.tracks)
    
    #Retorna una la lista de trayectorias ordenada de acuerdo al tiempo en que terminan
    def getSortedTracks(self):
        resultado=[]
        tmax=0
        for track in self.tracks:
            finTrack=track.puntos[len(track.puntos)-1].t#Tiempo final de la trayectoria
            if tmax<=finTrack:#Insertar al final
                resultado.append(track)
                tmax=track.puntos[len(track.puntos)-1].t
            else:#Insertar en otra parte
                aux=[]
                i=0
                while (finTrack>=resultado[i].puntos[len(resultado[i].puntos)-1].t):
                    aux.append(resultado[i])
                    i+=1
                aux.append(track)
                for j in range(i,len(resultado)):
                    aux.append(resultado[j])
                resultado=aux
        return resultado
                    
    def imprimir(self):
        for t in self.tracks:
            t.imprimir()
            print
    #Retorna el numero de frames
    def duracion(self):
        return max([track.puntos[len(track.puntos)-1].t for track in self.tracks])
        
    def guardar(self,ruta):
        f = file(ruta,'w')
        f.write('t')
        for track in self.tracks:
            f.write(',x,y,z,')
        
        for t in range(self.duracion+1):
            f.write('\n'+str(t))
            for track in self.tracks:
                x,y,z=track.posicion(t)
                if x:
                    f.write(','+str(x)+','+str(y)+','+str(z)+',')
                else:
                    f.write(',,,,')
        f.close()
    
    def puntos(self,tiempo,lmin):
        x2=[]
        y2=[]
        z2=[]
        for track in self.tracks:
            if lmin<=track.longitud():
                x1,y1,z1=track.posicion(tiempo)
                if x1!=None: 
                    x2.append(x1)
                    y2.append(y1)
                    z2.append(z1)
        return x2,y2,z2
    
    def vectores(self,tiempo,lmin):
        x=[]
        y=[]
        z=[]
        u=[]
        v=[]
        w=[]
        for track in self.tracks:
            x1,y1,z1=track.posicion(tiempo)
            x2,y2,z2=track.siguiente(tiempo)
            if x1 and x2 and lmin<=track.longitud:
                u1=x2-x1
                v1=y2-y1
                w1=z2-z1
                x.append(x1)
                y.append(y1)
                z.append(z1)
                u.append(u1)
                v.append(v1)
                w.append(w1)
        return x,y,z,u,v,w