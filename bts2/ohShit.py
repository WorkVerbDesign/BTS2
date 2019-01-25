import serial
import settings
import time
import consoleClass

speed = settings.serialSpeed
serialLoc = settings.serialAddy

reset = settings.pwr_cycle
homies = settings.homing
pullout = settings.pulloff_pos

def stopit():
    consoleClass.thread5 = "qick exit initiated"
    s = serial.Serial(serialLoc, speed)
    
    s.write(reset.encode())
    consoleClass.thread5 = "reset sent"
    
    time.sleep(2)
    s.write(homies.encode())
    consoleClass.thread5 = "homing"
    
    #s.write(pullout.encode())

if __name__ == "__main__":
    stopit()