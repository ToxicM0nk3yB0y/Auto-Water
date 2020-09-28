import RPi.GPIO as GPIO
import schedule
import time
import datetime
import json

with open('Settings.json') as json_file:
    settings = json.load(json_file)


#due to using schedule
#I want to make sure the file exists
# and see changes
def jsoncheck():
    print("json")

#basic idea of common informationt that can be pulled
### Test ###
def pull(plant):
    for p in settings['Plants'][plant]:
        p['LitersOfWater']
        p['P1LastDate']
        p['DaysToWait']


# set GPIO mode to look ath the PI pins 
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


# List of all channels
pinList = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]

# set up all channels

for i in pinList:
    GPIO.setup(i, GPIO.OUT)
    GPIO.output(i, GPIO.HIGH)


# Work out time need for volume
def V(L, PerX):
    return PerX * L 

#Variables
LiterPerX = 846.9
P1watertime = V(0.02, LiterPerX)
P1tubetime = 10
P1LastDate = datetime.datetime(2020, 9, 14)
P1WaitTime = 7



# Water Frist Plant
def WaterP1():
    GPIO.output(2, GPIO.LOW)
    # add it so that that data pulls from the json file
    time.sleep(P1watertime)
    print("water done")
    GPIO.cleanup(2)
       

def WaterP2():
    GPIO.output(17, GPIO.LOW)
    time.sleep(P1watertime)
    print("water done")
    GPIO.cleanup(17)
   

# converts last date water was printed on stored in json into timestamp
# then add (days to wait * 86400)
# if value is equal or greater than now
# then it activates the pump as per settings
def WhatsTheTime(LastDate, waitamount, water):
    now = datetime.datetime.now()
    Nwaitamount = waitamount * 86400
    if LastDate.timestamp() + Nwaitamount <= now.timestamp():
       eval(water)
       P1LastDate = datetime.datetime.now()


try:
    schedule.every().day.at("17:00").do(lambda : WhatsTheTime(P1LastDate, P1WaitTime, WaterP1()))
        
    
    while True:
        schedule.run_pending()
        time.sleep(1)

except KeyboardInterrupt:
    print("   Quite")
    GPIO.cleanup()
    pass
    
