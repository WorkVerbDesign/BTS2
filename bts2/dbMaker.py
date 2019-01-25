# Let's make an database
#
# this is like the worst code ever
#
# just to make an test DB for burn the subs
# returns the number of entries it creates.

from datetime import datetime, timedelta
from dataBaseClass import Sub
import os, time, random
import consoleClass

def makeDb():
    fileName = open("subscriberListTest.txt")
    count = 0

    for entry in fileName:

        entry = entry.strip()
        
        #fast
        dateTime = datetime.utcnow() + timedelta(seconds = count)
        
        count += 1
        dbEntry = Sub.create(
                                userName = entry,
                                entryTime = dateTime
                            )
        dbEntry.save()
        
        consoleClass.thread2 = str(count) + " entered to db"
            
        #slow    
        #consoleClass.thread4 = "added " + entry
        #time.sleep(random.randint(10,100)) #up to 10 seconds for testing
        #time.sleep(0.2)
    
    consoleClass.thread2 = str(count) + " entered to db, done you fuck"
    fileName.close()
    return count

if __name__ == "__main__":
    makeDb()