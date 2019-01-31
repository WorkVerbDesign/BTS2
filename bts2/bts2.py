#! /usr/bin/python3 
#   Module Runner
#   This is basically burn the subs

import settings
import sys
from threading import Thread
from time import sleep

from dataBaseClass import Sub, db
from placeAndGcode import placeNames, makeGcode
from sendGcode import gSend
from pubSubListener import ws1_start, pingTwitchServersToKeepTheConnectionAliveTask, webSocketInit
from frontPanel import Btn_Red, Btn_Blk, LED_BB_Red, LED_BB_Grn, LED_RB_Red, LED_Grn, LED_Red, LED_RB_Grn
from ohShit import stopit
import consoleClass
from consoleClass import consoleStuff

#for testing
#from dbMaker import makeDb 
#from dbUnparser import unParsify

#set flags
threadQuit = False
streamerToggle = False

#grab settings
entered = settings.nameEntered
placed = settings.namePlaced
gcode = settings.nameGcode
burnt = settings.nameBurnt

def runConsole():
    while not threadQuit:
        consoleStuff()
        
def runPlace():
    while not threadQuit:
        noNotPlaced = Sub.select().where(Sub.status==entered).count()
        
        if noNotPlaced > 0:
            placeNames()

def deraLict():
    noNotGd = Sub.select().where(Sub.status==placed).count()
        
    if noNotGd > 0:
        consoleClass.thread1 = "found " + str(noNotGd) + " un-gcoded names, fixing"
        gList = Sub.select().where(Sub.status==placed)
        for name in gList:
            makeGcode(name)
            
def testies():
    while not threadQuit:
        #number of names to process for the test
        entriesNo = Sub.select().where(Sub.status >= placed).count()
        
        #display number of names to process for the test
        consoleClass.thread1 = str(entriesNo)  + " of " + str(testicalNum)+ " names processed"
        
        #when all names have been placed end the test
        if testicalNum == entriesNo:
            endTheDamnTest()
            
def virtualSub():
    #virtual pubsub
    consoleClass.thread2 = "disabled for test"
    
    try:
        consoleClass.thread1 = "test: initiated. looking for db entries"
        chromazomes = Sub.select().where(Sub.status >= placed).count()
    except:
        consoleClass.thread1 = "test: making new db"
        chromazomes = 0
        
    chromazomes += makeDb()
    consoleClass.thread1 = "test: done adding names"

def endTheDamnTest():
    global threadQuit
    
    #console
    consoleClass.thread1 = "trying to exit clean!"
    
    #quit flag
    threadQuit = True
    
    #stop serial
    stopit()
    
    #put database gcode into text
    #unParsify()
    
    #stop the database
    db.stop()
    
    #indicate on the front panel
    LED_BB_Grn.on()
    sleep(2)
    LED_BB_Grn.off()
    
    #full exit of the program
    sys.exit()
    
def runBurner():    
    while not threadQuit: 
        readyCount = Sub.select().where(Sub.status==gcode).count()
        
        #console will update separately since this gets stuck in gSend.
        
        if readyCount > 0:           
            if readyCount >= 10:
                LED_Grn.blink()
                
            if readyCount < 10:
               LED_Grn.on() 
             
            if streamerToggle:
                gSend()
                
        else:
            LED_Grn.off()
        
                
def redButton():
    global streamerToggle

    LED_RB_Red.off()
    
    if streamerToggle == False:
        LED_RB_Grn.on()
        streamerToggle = True
        consoleClass.thread1 = "Sender Active"
    else:
        LED_RB_Grn.off()
        streamerToggle = False
        consoleClass.thread1 = "Sender Disabled"        
    
def blkButton():
    consoleClass.thread1 = "Shut down button pressed!"
    endTheDamnTest()

#these have to be declared here    
Btn_Red.when_released = redButton
Btn_Red.when_pressed = LED_RB_Red.on
Btn_Blk.when_pressed = LED_BB_Red.on
Btn_Blk.when_released = blkButton
            
if __name__ == "__main__":
    #console
    consoleClass.thread1 = "Burn the Subs Booted"

    try:  
        Thread.daemon = True

        #start console thread
        Thread(target=runConsole).start()
        
        #check if there are derelict entries
        deraLict()
        
        #pubSub, starts two threads
        webSocketInit()
        
        #testing virtualpubSub
        #virtualSub()
        
        #placer
        Thread(target=runPlace).start()
        
        #testing thread trap
        #testies(chromazomes)
        
        #gCodeStreamer, traps thread
        runBurner()

        
    except KeyboardInterrupt:
        endTheDamnTest()
    except:
        LED_Red.on()