'''
Created on 6 sept. 2017

@author: Fab
'''
import sqlite3
from time import *
from database.Chronometer import Chronometer
from database.Animal import *
from database.Detection import *
from database.Measure import *
import matplotlib.pyplot as plt
import numpy as np
from database.Event import *

class Train2():
    
    def __init__(self, idA, idB ):
        self.idA = idA
        self.idB = idB

def reBuildEvent( connection, tmin=None, tmax=None ): 
    '''
    three animals are following each others with nose-to-anogenital contacts
    animals are moving
    
    this is a combination of Train2 events (train2 events must be calculated before this event)
    '''

    deleteEventTimeLineInBase(connection, "Train4" )

    pool = AnimalPool( )
    pool.loadAnimals( connection )
    pool.loadDetection( start = tmin, end = tmax )

    ''' build a list of train 2 for each time point '''
    
    time = {}
    train4 = {}
    
    for idAnimalA in range( 1, 5 ):
        for idAnimalB in range( 1 , 5 ):
            if ( idAnimalA == idAnimalB ):
                continue
            train2TimeLine = EventTimeLine( connection, "Train2", idAnimalA, idAnimalB, minFrame=tmin, maxFrame=tmax )
            for t in train2TimeLine.getDictionnary():
                train = Train2( idAnimalA, idAnimalB )
                
                if ( not t in time ):
                    time[t] =[]
                    
                print ( t , ":" , train.idA , " -> ", train.idB , "*" )
                time[t].append( train )
    

    for t in time:
        trainList = time[t]
        
        for train1st in trainList:
            
            for train2nd in trainList:
                
                if ( train1st == train2nd ):
                    continue

                for train3rd in trainList:
                    
                    if ( train3rd == train1st or train3rd == train2nd):
                        continue
                    
                    isValid = ""
                    ''' test chain link between train2 events '''
                   
                    if train1st.idB == train2nd.idA and train2nd.idB == train3rd.idA :
                        
                        id1 = train1st.idA
                        id2 = train1st.idB
                        id3 = train2nd.idB
                        id4 = train3rd.idB
    
                        if not (id1, id2, id3,id4) in train4:    
                            train4[id1,id2,id3,id4] = {} 
                        
                        train4[id1,id2,id3,id4][t]=True
                        
                        isValid = ": validated train 4"
                    print ( t , ":" , train1st.idA , " -> ", train1st.idB, "--->", train2nd.idA , " -> ", train2nd.idB , " -> ", train3rd.idA , " -> ", train3rd.idB , isValid )


    ''' save data '''
            
    for idAnimalA in range( 1 , 5 ):
    
        for idAnimalB in range( 1 , 5 ):
            
            for idAnimalC in range( 1 , 5 ):

                for idAnimalD in range( 1 , 5 ):

                    if (idAnimalA, idAnimalB, idAnimalC, idAnimalD) in train4:
                        
                        trainTimeLine = EventTimeLine( None, "Train4" , idAnimalA , idAnimalB, idAnimalC, idAnimalD, loadEvent=False )
                        
                        trainTimeLine.reBuildWithDictionnary( train4[idAnimalA,idAnimalB,idAnimalC,idAnimalD] )
                        #trainTimeLine.removeEventsBelowLength( 5 )            
                        trainTimeLine.endRebuildEventTimeLine(connection)
                    
        
    # log process
    from database.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Train4" , tmin=tmin, tmax=tmax )

    print( "Rebuild event finished." )
    
    return
   
    
    