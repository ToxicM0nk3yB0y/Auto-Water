#import RPi.GPIO as GPIO
import json
import sched, time
import schedule
from datetime import datetime, timedelta


sc = sched.scheduler(time.time, time.sleep)


with open('D:\Projects\Coding\Python\Auto-Water\Settings.json') as json_file:
    jobs = json.load(json_file)



def update():
    return

def water(plant):
    literPerX = jobs['Pump']['LiterPerX']
    for job in jobs['Plants']:
        # is job still active before attempting?                                   is jop a minimum of 20 minutes late?
        if jobs['Plants'][job]['Status'] == "Active" and datetime.strptime( jobs['Plants'][job]['NextEvent'] , '%Y-%m-%dT%H:%M:%S.%f%z') <= (datetime.now() + timedelta(minutes=20)):
            # turn on the relay for the pump give via json GPIO
            
            #GPIO.output(jobs['Plants'][job]['GPIO'], GPIO.LOW)
            print("Turn on motor")
            
            #update the json for last done job
            update(datetime.now())
            # cal liters want by time per liter from json
            time.sleep(jobs['Plants'][job]['LitersOfWater'] * literPerX )
            # let the user know its done
            print("water done")
            #turn off sheet
            
            #GPIO.cleanup(jobs['Plants'][job]['GPIO'])
            print("Turn off motor")

            
            

def WaitTime(nextevent, daystoWait, timetoWater, lastEvent, defaultTime):
    # take current time
    now = datetime.now()

    #has date set for next time to event
    if nextevent != 0:
        # convert nextevent string into date
        nexteventDate = datetime.strptime(nextevent , '%Y-%m-%dT%H:%M:%S.%f%z')
        #check if its today
        if nexteventDate.date == now.date:
            #return true & the time till event today
            return True, nexteventDate.timestamp() - now.timestamp()
        else:
            #if its not today return false
            return False
            
    # check if DaysToWait and TimeToWater(24h) are blak
    if daystoWait != '' and timetoWater != '':

        #if watering time or days to wait has been missed, time is equal to defaultTime and done today
        if timetoWater == '':
            if datetime.strptime(lastEvent, '%d/%m/%Y') + timedelta(days=daystoWait) <= datetime.now():
                T = defaultTime.split(":")
                h = int(str(T[0]))
                m = int(str(T[1]))

                nowr = now.replace(hour=h,minute=m,second=0,microsecond=0)
                result = nowr.timestamp() - now.timestamp()
                
                # return true and the time to wait
                return True, result
                #update('NextEvent', nowr)
            else: return False, 0
            
        
        #spliting out clock time for TimtToWater(24h)
        T = timetoWater.split(":")
        h = int(str(T[0]))
        m = int(str(T[1]))
        
        #check if LastEvent is blank
        if lastEvent != "": 
            # see if its over due
            if (datetime.strptime(lastEvent, '%d/%m/%Y') + timedelta(days=daystoWait)) <= datetime.today():
                nowr = now.replace(hour=h,minute=m,second=0,microsecond=0)
                result = nowr.timestamp() - now.timestamp()
                # return true and the time to wait
                return True, result
                #update('NextEvent', nowr)
            else: return False, 0
        
        #check if the days to wait is missing too
        elif daystoWait == '':
            if datetime.strptime(lastEvent, '%d/%m/%Y') <= datetime.now():
                T = timetoWater.split(":")
                h = int(str(T[0]))
                m = int(str(T[1]))

                nowr = now.replace(hour=h,minute=m,second=0,microsecond=0)
                result = nowr.timestamp() - now.timestamp()
                
                # return true and the time to wait
                return True, result
                #update('NextEvent', nowr)
            else: return False, 0
        
        else: 
            nowr = now.replace(hour=h,minute=m,second=0,microsecond=0)
            result = nowr.timestamp() - now.timestamp()
            update("LastEvent", nowr.date)
            return result

    else:             
        if datetime.strptime(lastEvent, '%d/%m/%Y') <= datetime.now():
            T = defaultTime.split(":")
            h = int(str(T[0]))
            m = int(str(T[1]))

            nowr = now.replace(hour=h,minute=m,second=0,microsecond=0)
            result = nowr.timestamp() - now.timestamp()
            
            # return true and the time to wait
            return True, result
            #update('NextEvent', nowr)
        else: return False, 0





def load_Jobs():
    for job in jobs['Plants']:
        if jobs['Plants'][job]['Status'] == "Active":
            sjob = jobs['Plants'][job]
            # is NextEvent blank?
            if sjob['NextEvent'] == "":
                # if end_date.date <> now.date;
                result = WaitTime(0, sjob['DaysToWait'], sjob['TimeToWater(24h)'], sjob['LastEvent'], jobs['default']['TimeToWater(24h)'])
                if result[0] == True:
                    # scheduling watering for set delay
                    # result[1] = seconds to wait, water is func and job is var for Plant ref
                    sc.enter(result[1], 1, water, argument=(job,))
                    print("time to wait; " + str(result[1]) + " for;"  + job)
                elif result[0] == False:
                    continue
            else: 
                # if end_date.date <> now.date;
                result = WaitTime(sjob['NextEvent'], '', '')
                if result[0] == True:
                    # scheduling watering for set delay
                    # result[1] = seconds to wait, water is func and job is var for Plant ref
                    schedule.enterabs(result[1], 1, water, job) 





try:
    #schedule.every().day.at("23:16").do(load_Jobs)
    load_Jobs()
    sc.run()

    while True:
        schedule.run_pending()
        time.sleep(1)

except KeyboardInterrupt:
    print("   Quite")
    #GPIO.cleanup()
    pass