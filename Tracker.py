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
        for i in range(len(datos)):
            r=Track()
            if i%100==0:
                print i,'/',len(datos)
            for vals  in datos[i]:
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
    
    def puntos(self,tiempo,lmin,xc= np.inf):
        x2=[]
        y2=[]
        z2=[]
        for track in self.tracks:
            x1,y1,z1=track.posicion(tiempo)
            x3,y3,z3=track.siguiente(tiempo)
            if x1 and x3 and lmin<=track.longitud():
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
            if x1 and x2 and lmin<=track.longitud():
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
        
    def sentidos(self,xc,yc,lmin):
        def sentidosT(tiempo):
            def determinarSentido(x3,y3,z3,x4,y4,z4):
                distActual=(x3-xc)**2+(y3-yc)**2#Distancia actual al centro
                distSiguiente=(x4-xc)**2+(y4-yc)**2#Dist. siguiente al centro
                deltaRadial=distSiguiente-distActual#Desplazamiento radial
                deltaZ = z4-z3#Desplazamiento z
                if deltaRadial>0:
                    return 1
                else:
                    return 0
                
            
            resultado=[]
            for track in self.tracks:
                x3,y3,z3=track.posicion(tiempo)
                x4,y4,z4=track.siguiente(tiempo)
                if x3 and x4 and lmin<=track.longitud():
                    resultado.append(determinarSentido(x3,y3,z3,x4,y4,z4))
            return resultado
        return [sentidosT(t) for t in range(self.duracion)]
    """
    def vectoresSeparados(self,xc,yc,tiempo,lmin):
        "Retorna los vectores separados por su sentido (centro, fuera, arriba, abajo)"
        x1=[]
        y1=[]
        z1=[]
        u1=[]
        v1=[]
        w1=[]
        x2=[]
        y2=[]
        z2=[]
        u2=[]
        v2=[]
        w2=[]
        for track in self.tracks:
            x3,y3,z3=track.posicion(tiempo)
            x4,y4,z4=track.siguiente(tiempo)
            if x3 and x4 and lmin<=track.longitud:
                hypOrigen=(x3-xc)**2+(y3-yc)**2
                hypDest=(x4-xc)**2+(y4-yc)**2
                u3=x4-x3
                v3=y4-y3
                w3=z4-z3
                if (hypOrigen>hypDest):#Si se acerca al centro...
                    x1.append(x3)
                    y1.append(y3)
                    z1.append(z3)
                    u1.append(u3)
                    v1.append(v3)
                    w1.append(w3)
                else:
                    x2.append(x3)
                    y2.append(y3)
                    z2.append(z3)
                    u2.append(u3)
                    v2.append(v3)
                    w2.append(w3)
        return x1,y1,z1,u1,v1,w1,x2,y2,z2,u2,v2,w2"""