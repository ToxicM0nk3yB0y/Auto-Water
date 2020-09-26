import RPi.GPIO as GPIO
import schedule
import time
import datetime



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
    #time.sleep(P1tubetime)
    #print("tubes full")
    time.sleep(P1watertime)
    print("water done")
    #time.sleep(P1tubetime)
    #print("tubes Empty")
    GPIO.cleanup(2)
       

def WaterP2():
    GPIO.output(17, GPIO.LOW)
    #time.sleep(P1tubetime)
    #print("tubes full")
    time.sleep(P1watertime)
    print("water done")
    #time.sleep(P1tubetime)
    #print("tubes Empty")
    GPIO.cleanup(17)
   
fun = locals()

def WhatsTheTime(LastDate, waitamount, water):
    now = datetime.datetime.now()
    if now.day + waitamount <= LastDate.day:
       eval(water)
       P1LastDate = datetime.datetime.now()
    



#WaterP1()
#WaterP2()

try:
    schedule.every().day.at("17:00").do(lambda : WhatsTheTime(P1LastDate, P1WaitTime, WaterP1()))
        
    
    while True:
        schedule.run_pending()
        time.sleep(1)

except KeyboardInterrupt:
    print("   Quite")
    GPIO.cleanup()
    pass
    
