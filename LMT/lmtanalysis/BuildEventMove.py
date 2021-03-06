'''
Created on 6 sept. 2017

@author: Fab
'''
import sqlite3
from time import *
from lmtanalysis.Chronometer import Chronometer
from lmtanalysis.Animal import *
from lmtanalysis.Detection import *
from lmtanalysis.Measure import *
import matplotlib.pyplot as plt
import numpy as np
from lmtanalysis.Event import *
from lmtanalysis.Measure import *
from lmtanalysis.EventTimeLineCache import EventTimeLineCached

def flush( connection ):
    ''' flush event in database '''
    deleteEventTimeLineInBase(connection, "Move" )
    deleteEventTimeLineInBase(connection, "Move isolated" )
    deleteEventTimeLineInBase(connection, "Move in contact" )


def reBuildEvent( connection, file, tmin=None, tmax=None, pool = None  ):
    
    ''' 
    Animal A is stopped (built-in event):
    Move social: animal A is stopped and in contact with any other animal.
    Move isolated: animal A is stopped and not in contact with any other animal.
    ''' 
    
    pool = AnimalPool( )
    pool.loadAnimals( connection )
    
    isInContactSourceDictionnary = {}
    moveSourceTimeLine = {}
    
    for idAnimalA in range( 1 , pool.getNbAnimals()+1 ):
        ''' Load source stop timeLine and revert it to get the move timeline
        If the animal is not detected, this will result in a move. To avoid this we mask with the detection.
        '''
        moveSourceTimeLine[idAnimalA] = EventTimeLine( connection, "Stop", idAnimalA, minFrame=tmin, maxFrame=tmax, inverseEvent=True )
        detectionTimeLine = EventTimeLine( connection, "Detection", idAnimalA, minFrame=tmin, maxFrame=tmax )
        moveSourceTimeLine[idAnimalA].keepOnlyEventCommonWithTimeLine( detectionTimeLine )
        
        ''' load contact dictionnary with whatever animal '''
        isInContactSourceDictionnary[idAnimalA] = EventTimeLineCached( connection, file, "Contact", idAnimalA, minFrame=tmin, maxFrame=tmax ).getDictionnary()
                    
    
    for idAnimalA in range( 1 , pool.getNbAnimals()+1 ):

        moveSocialResult = {}
        moveIsolatedResult = {}
        
        ''' loop over eventlist'''
        for moveEvent in moveSourceTimeLine[idAnimalA].eventList:
        
            ''' for each event we seek in t and search a match in isInContactDictionnary '''
            for t in range ( moveEvent.startFrame, moveEvent.endFrame+1 ) :
                if t in isInContactSourceDictionnary[idAnimalA]:
                    moveSocialResult[t] = True
                else:
                    moveIsolatedResult[t] = True
    
        ''' save move '''
        moveResultTimeLine = EventTimeLine( None, "Move" , idAnimalA , None , None , None , loadEvent=False )
        moveResultTimeLine.reBuildWithDictionnary( moveSourceTimeLine[idAnimalA].getDictionnary() )
        moveResultTimeLine.endRebuildEventTimeLine(connection)

        ''' save move isolated '''
        moveIsolatedResultTimeLine = EventTimeLine( None, "Move isolated" , idAnimalA , None , None , None , loadEvent=False )
        moveIsolatedResultTimeLine.reBuildWithDictionnary( moveIsolatedResult )
        moveIsolatedResultTimeLine.endRebuildEventTimeLine(connection)

        ''' save move social '''
        moveSocialResultTimeLine = EventTimeLine( None, "Move in contact" , idAnimalA , None , None , None , loadEvent=False )
        moveSocialResultTimeLine.reBuildWithDictionnary( moveSocialResult )
        moveSocialResultTimeLine.endRebuildEventTimeLine(connection)

        
    # log process
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Move" , tmin=tmin, tmax=tmax )
                       
    print( "Rebuild event finished." )
        
    