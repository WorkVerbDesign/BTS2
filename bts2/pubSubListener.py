import websocket, threading, time, json, random, re
import settings
import codes #py file containing secret keys and ID info
from dataBaseClass import Sub
from datetime import datetime
from frontPanel import LED_Blue
import consoleClass

#make sure to install the websocket module with: sudo pip3 install websocket-client

#to get user id: https://api.twitch.tv/kraken/users/<name>?client_id=apitoken
#to get channel id: https://api.twitch.tv/kraken/channels/<name>?client_id=apitoken

#user name vs display name:
#need to check if display name has non ^[a-zA-Z0-9_]{4,25}$ chars use username instead 

pingstarttime = 0
pingTwitch = 0
SUBdidWork = 0

twitchOAuthToken = codes.twitchOAuth # this is generated at https://twitchapps.com/tokengen/ with scope "channel_subscriptions" and the api token from the dev dasboard
channelID = codes.channelID #oh_bother number code
userID = settings.pubSubUserId #lebtvlive

#e4t5v345nz3sm is just a unique code we set to check for in the return from twitch
#listenrequest = {"type": "LISTEN", "nonce": "e4t5v345nz3sm", "data": { "topics": ["whispers." + userID], "auth_token": twitchOAuthToken}} #this is what i tested it with for whisper messages
listenrequest = {"type": "LISTEN", "nonce": "e4t5v345nz3sm", "data": { "topics": ["channel-subscribe-events-v1." + channelID], "auth_token": twitchOAuthToken}} #this is for sub events
ws1 = ""

#log file
loggies = settings.wsLogFile

def ws1_on_message(ws, message):
    jsonReturn = json.loads(message)
    
    #log file
    logOutput = open(loggies, "a")
    logOutput.write(datetime.utcnow().strftime('%Y,%m,%d,%H:%M:%S:%f'))
    logOutput.write(" raw message: ")
    logOutput.write(message)
    logOutput.write("\n")
    logOutput.close()
    
    if "type" in jsonReturn:
    
        #Take care of pong responses
        if jsonReturn["type"] == "PONG": 
            pingstarttime = 0
            
            #console
            consoleClass.thread2 = "Pinging Twitch, pong'd"
            
            #front panel
            LED_Blue.on()
        
        #Close if twitch tells us so and reconnect        
        elif jsonReturn["type"] == "RECONNECT":            
            #console
            consoleClass.thread2 = "Reconnect!"
            
            try:
                ws.close()
            except:
                pass
       
        #We get this as a response to our subToTopic request
        elif jsonReturn["type"] == "RESPONSE": 
        
            #validate this is the right response and there was no error
            if jsonReturn["nonce"] == "e4t5v345nz3sm" and jsonReturn["error"] == "": 
                #console
                consoleClass.thread2 = "good nonce"
                
                SUBdidWork = 1
                
            #If there was something wrong    
            else:
                #console
                consoleClass.thread2 = "JSON response error!?"
                
        #This is the message you get when an event itself happens (a sub event) 
        elif jsonReturn["type"] == "MESSAGE": 
            #print(jsonReturn["data"]["message"])
            makeEntry(json.loads(jsonReturn["data"]["message"]))
            
        else:
            #if there is anything else, shouldn't be
            consoleClass.thread2 = "JSON message error!?"

#check to see if we're using user name or account name
def makeEntry(message):
    #log file
    logOutput = open(loggies, "a")
    logOutput.write(datetime.utcnow().strftime('%Y,%m,%d,%H:%M:%S:%f'))
    logOutput.write(" ")
    logOutput.write(json.dumps(message))
    logOutput.write('\n')
    logOutput.write(datetime.utcnow().strftime('%Y,%m,%d,%H:%M:%S:%f'))
    
    #name checker
    #gift sub handler
    if 'recipient_user_name' in message.keys():
        repName = message['recipient_display_name']
        repUser = message['recipient_user_name']
        
        if checkName(repName):
            enterDb(repName)
            logOutput.write("using repName: " + repName)
            #print(repName)
        else:
            enterDb(repUser)
            logOutput.write("using repUser: " + repUser)
            #print(repUser)
            
    #regular sub handler
    else:
        dispName = message['display_name']
        usrName = message['user_name']

        if checkName(dispName):
            enterDb(dispName)
            logOutput.write("using dispName: " + dispName)
            #print(dispName)
        else:
            enterDb(usrName)
            logOutput.write("using usrName: " + usrName)
            #print("fuck you buddy")
            
    #this is probably where a "doesn't fit either wtf" message goes
            
    #close the log
    logOutput.write("\n")            
    logOutput.close()
    
#see if the name meets requirements
def checkName(name):
    if re.search(r'[^a-zA-Z0-9_]', name):
        return False
    else:
        return True

#enter the data into the database        
def enterDb(entry):

    #console
    consoleClass.thread2 = entry + " received"
    
    dateInfo = datetime.utcnow()
    dbEntry = Sub.create(
                        userName = entry,
                        entryTime = dateInfo
                    )
    dbEntry.save()

#called on a websocket connection error
def ws1_on_error(ws, error): 
    global pingTwitch, SUBdidWork
    pingTwitch = 0
    SUBdidWork = 0
    LED_Blue.blink()
    
    #console
    consoleClass.thread2 = "WEBSOCKET ERROR"
    
    #log file
    logOutput = open(loggies, "a")
    logOutput.write(datetime.utcnow().strftime('%Y,%m,%d,%H:%M:%S:%f'))
    logOutput.write(" ws1 error: ")
    logOutput.write(error)
    logOutput.write("\n")
    logOutput.close()

#called when the websocket is closed
def ws1_on_close(ws):
    global pingTwitch, SUBdidWork
    
    pingTwitch = 0
    SUBdidWork = 0
    LED_Blue.off()
    
    #console
    consoleClass.thread2 = "closing websocket"
    
    #log file
    logOutput = open(loggies, "a")
    logOutput.write(datetime.utcnow().strftime('%Y,%m,%d,%H:%M:%S:%f'))
    logOutput.write(" ws1 closed\n")
    logOutput.close()

#called when the websocket connection is opened
def ws1_on_open(ws): 
    global pingTwitch
    consoleClass.thread2 = "websocket opening"
    
    pingTwitch = 1
    
    #log file
    logOutput = open(loggies, "a")
    logOutput.write(datetime.utcnow().strftime('%Y,%m,%d,%H:%M:%S:%f'))
    logOutput.write(" ws1 opened\n")
    logOutput.close()
    
    #sub to topic engine
    subToTopics()
    
    
#this is the main server loop
def ws1_start(): 
    while True:
        #console
        consoleClass.thread2 = "websocket startup"
        
        #log file
        logOutput = open(loggies, "a")
        logOutput.write(datetime.utcnow().strftime('%Y,%m,%d,%H:%M:%S:%f'))
        logOutput.write(" ws1 restart\n")
        logOutput.close()
        
        #ping engine
        ws1.run_forever()

#send our listen request
def subToTopics(): 
    #console
    consoleClass.thread2 = "subbing to topic"
    
    #sub to topic
    ws1.send(json.dumps(listenrequest))

#Ping the server every 4 mins +- 10 sec as per twitch API requirement
def pingTwitchServersToKeepTheConnectionAliveTask(): 
    while True:
        if pingTwitch:
            #console
            consoleClass.thread2 = "Pinging Twitch"
            
            #ping twitch
            ws1.send(json.dumps({"type": "PING"}))
            pingstarttime = time.time() #we could later do something with this time but we don't have to
            
            #front panel
            LED_Blue.off()
            
            #console
            consoleClass.thread2 = "Pinging Twitch, waiting for response"
            
            #wait 10 sec for ping response
            time.sleep(10)
            
            #if pingstarttime was not reset, close the connection
            if not pingstarttime: 
                consoleClass.thread2 = "start time was not reset?"
                ws.close()
                
            #this is for the console readout + ping timer
            countdown = 240 + random.randrange(-10, 10)
            
            while countdown >= 0:
                #might want to make mm:ss time format here
                
                #console
                consoleClass.thread2 = "Next Ping in " + countdown
                
                #new timer
                time.sleep(1)
                countdown -= 1
                
            #time.sleep(240 + random.randrange(-10, 10)) #Sleep 4 min +/- 10sec (random is required by twitch api)

def webSocketInit():
    global ws1
    print("pubSub started, opening socket")

    #console
    consoleClass.thread2 = "pubSub Started"
    
    #log file
    logOutput = open(loggies, "a")
    logOutput.write(datetime.utcnow().strftime('%Y,%m,%d,%H:%M:%S:%f'))
    logOutput.write(" pubSub Started\n")
    logOutput.close()

    ws1 = websocket.WebSocketApp("wss://pubsub-edge.twitch.tv", on_message = ws1_on_message, on_error = ws1_on_error, on_close = ws1_on_close) #Create Websocket Client Object
    ws1.on_open = ws1_on_open
    threading.Thread(target=ws1_start).start() #Start Websocket Thread
    threading.Thread(target=pingTwitchServersToKeepTheConnectionAliveTask).start() # Start PING Thread
 
if __name__ == "__main__":
    webSocketInit()
    threading.Thread(target=ws1_start).start() #Start Websocket Thread
    threading.Thread(target=pingTwitchServersToKeepTheConnectionAliveTask).start() # Start PING Thread
