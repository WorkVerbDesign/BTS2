#! /usr/bin/python3 
#   Module Runner
#   This is basically burn the subs

import settings
import sys
from threading import Thread
from time import sleep

from dataBaseClass import Sub, db
from placeNoGcode import placeNames
from makePng import makeOnePng

from dbMaker import makeDb
import consoleClass

threadQuit = False

entered = settings.nameEntered
placed = settings.namePlaced
gcode = settings.nameGcode
burnt = settings.nameBurnt


def runPlace():
    while not threadQuit:
        noNotPlaced = Sub.select().where(Sub.status==entered).count()
        
        if noNotPlaced > 0:
            placeNames()
            
def testies(testicalNum):
    while not threadQuit:
        entriesNo = Sub.select().where(Sub.status >= placed).count()
        consoleClass.thread1 = str(entriesNo)  + " of " + str(testicalNum)+ " names processed"
        if testicalNum == entriesNo:
            endTheDamnTest()
   
   
def endTheDamnTest():
    global threadQuit
    
    consoleClass.thread1 = "trying to exit clean!"
    
    threadQuit = True
    #stopit()
    #unParsify()
    makeOnePng()
    
    db.stop()
    #LED_BB_Grn.on()
    #sleep(2)
    #LED_BB_Grn.off()
    sys.exit() 
    
if __name__ == "__main__":
    consoleClass.thread1 = "Octo special Burn the Subs started"
    
    try:
        Thread.daemon = True
        consoleClass.consoleStuff()
        
        #check if there are derelict entries
        #deraLict()
        
        #pubSub
        #webSocketInit()
        
        #virtual pubsub
        try:
            consoleClass.thread4 = "looking for db entries"
            chromazomes = Sub.select().where(Sub.status >= placed).count()
        except:
            consoleClass.thread4 = "making new db"
            chromazomes = 0
            
        chromazomes += makeDb()
        consoleClass.thread4 = "done adding names"
        
        #placer
        #runPlace()
        Thread(target=runPlace).start()
        
        #thread trap
        testies(chromazomes)
        #Thread(target=testies).start()
        #Thread.daemon = True

        #gCodeStreamer
        #runBurner()
    except KeyboardInterrupt:
        endTheDamnTest()