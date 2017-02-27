from Tracker import Tracks

class VelocityFields:
    def __init__(self,tracks,deltaX,deltaY,deltaZ,overlapX=0.5,overlapY=0.5,overlapZ=0.5):
        self.tracks=tracks
        if deltaX>0 and deltaY>0 and deltaZ>0 and overlapX>0 and overlapY>0 and overlapZ>0:
            self.deltaX=deltaX
            self.deltaY=deltaY
            self.deltaZ=deltaZ
            if overlapX<1 and overlapY<1 and overlapZ<1:
                self.overlapX=overlapX
                self.overlapY=overlapY
                self.overlapZ=overlapZ
        
    def calc(self):
        xmin=0
        xmax=self.deltaX
        ymin=0
        ymax=self.deltaY
        zmin=-4
        zmax=zmin+self.deltaZ
        
        