# console class
# using blessings
# should also be wary of resizing
# and dropping in screen mid-session

from blessings import Terminal
from datetime import datetime
from threading import Timer
import time
from dataBaseClass import Sub
import os
import settings

t = Terminal()

thread1 = "init"
thread2 = "init"
thread3 = "init"
thread4 = "init"
thread5 = "init"

#fixed vars
entered = settings.nameEntered
placed = settings.namePlaced
gcode = settings.nameGcode
burnt = settings.nameBurnt

def consoleStuff():
    degreesSomething = os.popen("vcgencmd measure_temp").readline()
    degreesSomething = degreesSomething.replace("temp=","")
    enterCount = Sub.select().where(Sub.status==entered).count()
    placeCount = Sub.select().where(Sub.status==placed).count()
    readyCount = Sub.select().where(Sub.status==gcode).count()
    burntCount = Sub.select().where(Sub.status==burnt).count()
  
    print(t.clear())
    print(t.bold("Main: ") + thread1)
    print(t.bold("PubSub: ") + thread2)
    print(t.bold("Placer: ") + thread3)
    print(t.bold("Maker: ") + thread4)
    print(t.bold("Sender: ") + thread5)    
    
    #stat readout
    print(str(enterCount) + " en | " + str(placeCount) + " pl | " + str(readyCount) + " rdy | " + str(burntCount) + " burnd")
    print(degreesSomething)
    
    
    #time at bottom of screen
    #want this to be uptime but meh
    now = datetime.utcnow()
    print(str(now))
    
    #no more of this billion thread crap
    #garbage = Timer(1, consoleStuff).start()
    time.sleep(1)
    
if __name__ == "__main__":
    consoleStuff()