#import RPi.GPIO as GPIO
import json
import sched, time
import schedule
from datetime import datetime, timedelta


sc = sched.scheduler(time.time, time.sleep)
jsonFile =  'D:\Projects\Coding\Python\Auto-Water\Settings.json'

with open(jsonFile) as json_file:
    jobs = json.load(json_file)


def update(section, value,  plant ):

    # update the json file when values change
    #for Examples NextEvent or LastEvent
    with open(jsonFile, 'r') as file:
        json_data = json.load(file)
        if isinstance(value, datetime): 
            if section == "LastEvent": json_data["Plants"][plant][section] = datetime.strftime(value.date() , '%d/%m/%Y')
            else: json_data["Plants"][plant][section] = datetime.strftime(value , '%d/%m/%Y %H:%M:%S')
        else: json_data["Plants"][plant][section] = value
            
    file.close

    with open(jsonFile, 'w') as file:
        json.dump(json_data, file, indent=2)


def timesplit(value):
    try:
        T = value.split(":")
        return int(str(T[0])), int(str(T[1]))
    
    except ValueError:
        T = jobs['default']['TimeToWater(24h)'].split(":")
        return int(str(T[0])), int(str(T[1]))

def returnseconds(new, now):
    T = timesplit(jobs['default']['TimeToWater(24h)'])
    if new.timestamp() - now.timestamp() <= 0: return now.replace(hour=T[0],minute=T[1],second=0,microsecond=0).timestamp() - now.timestamp(), True
    else: new.timestamp() - now.timestamp(), False

    




def water(plant):
    literPerX = jobs['Pump']['LiterPerX']
    # is job still active before attempting?                                   is job a minimum of 20 minutes late?
    #if jobs['Plants'][plant]['Status'] == "Active" and datetime.strptime( jobs['Plants'][plant]['NextEvent'] , '%Y-%m-%dT%H:%M:%S.%f%z') <= (datetime.now() + timedelta(minutes=20)):
    # turn on the relay for the pump give via json GPIO
    #GPIO.output(jobs['Plants'][job]['GPIO'], GPIO.LOW)
    print("Turn on motor")
    
    # cal liters want by time per liter from json
    time.sleep(jobs['Plants'][plant]['LitersOfWater'] * literPerX )
    # let the user know its done
    print("water done")
    #turn off sheet
    
    #GPIO.cleanup(jobs['Plants'][job]['GPIO'])
    print("Turn off motor")

    jobathand = jobs['Plants'][plant]

    daystoWait = jobathand['DaysToWait']
    TimeToWater = jobathand['TimeToWater(24h)']
    defaultTime = jobs['default']['TimeToWater(24h)']

    if daystoWait == "": daystoWait = 1

    
    try:
        T = TimeToWater.split(":")
        h = int(str(T[0]))
        m = int(str(T[1]))
    except ValueError:
        T = defaultTime.split(":")
        h = int(str(T[0]))
        m = int(str(T[1]))
    

    newdate = datetime.now() + timedelta(days=daystoWait) 
    #update NextEvent
    update('NextEvent', newdate.replace(hour=h,minute=m,second=0,microsecond=0), plant)

    #update the json for last done job
    update("LastEvent", datetime.now(), plant)

            
            

def WaitTime(nextevent, daystoWait, timetoWater, lastEvent, defaultTime, plant):
    # take current time
    now = datetime.now()

    #has date set for next time to event
    if nextevent != '':
        
        #re-cal the date
        T = timesplit(timetoWater)

        nowr = datetime.strptime(lastEvent, '%d/%m/%Y') + timedelta(days=daystoWait)

        #check if its today
        if nowr.date() <= now.date():
            #return true & the time till event today
            result = returnseconds(nowr, now)
            if result[1] == True: 
                T = timesplit(defaultTime)
                update('NextEvent', nowr.replace(day=now.date().day,hour=T[0],minute=T[1],second=0,microsecond=0), plant)
            return True, result[0]
        else:
            #if its not today return false
            update('NextEvent', nowr.replace(hour=T[0],minute=T[1],second=0,microsecond=0), plant)
            return False, 0
            
    # check if DaysToWait and TimeToWater(24h) are blak
    if daystoWait != '' and timetoWater != '':

        T = timesplit(timetoWater)

        nowr = datetime.strptime(lastEvent, '%d/%m/%Y') + timedelta(days=daystoWait)
        update('NextEvent', nowr.replace(hour=T[0],minute=T[1],second=0,microsecond=0), plant)

        #if watering time or days to wait has been missed, time is equal to defaultTime and done today
        if timetoWater == '':
            if datetime.strptime(lastEvent, '%d/%m/%Y') + timedelta(days=daystoWait) <= datetime.now():
                T = timesplit(defaultTime)

                nowr = now.replace(hour=T[0],minute=T[1],second=0,microsecond=0)
                result = returnseconds(nowr, now)
                
                update('NextEvent', nowr, plant)

                # return true and the time to wait
                return True, result
                
            else: return False, 0
            
        
        #spliting out clock time for TimtToWater(24h)
        T = timesplit(timetoWater)
        
        #check if LastEvent is blank
        if lastEvent != "": 
            # see if its over due
            if (datetime.strptime(lastEvent, '%d/%m/%Y') + timedelta(days=daystoWait)) <= datetime.today():
                nowr = now.replace(hour=T[0],minute=T[1],second=0,microsecond=0)
                result = returnseconds(nowr, now)

                update('NextEvent', nowr, plant)
                update('LastEvent', nowr.date(), plant)

                # return true and the time to wait
                return True, result

            else: return False, 0
        
        #check if the days to wait is missing too
        elif daystoWait == '':
            if datetime.strptime(lastEvent, '%d/%m/%Y') <= datetime.now():
                T = timesplit(timetoWater)

                nowr = now.replace(hour=T[0],minute=T[1],second=0,microsecond=0)
                result = returnseconds(nowr, now)
                
                update('NextEvent', nowr, plant)

                # return true and the time to wait
                return True, result
                
            else: return False, 0
        
        else: 
            nowr = now.replace(hour=T[0],minute=T[1],second=0,microsecond=0)
            result = returnseconds(nowr, now)
            update("LastEvent", nowr, plant)
            return result

    else:             
        if datetime.strptime(lastEvent, '%d/%m/%Y') <= datetime.now():
            T = timesplit(defaultTime)

            nowr = now.replace(hour=T[0],minute=T[1],second=0,microsecond=0)
            result = returnseconds(nowr, now)
            
            update('NextEvent', nowr, plant)

            # return true and the time to wait
            return True, result
            
        else: return False, 0





def load_Jobs():
    for job in jobs['Plants']:
        if jobs['Plants'][job]['Status'] == "Active":
            sjob = jobs['Plants'][job]
            # is NextEvent blank?
            if not bool(sjob['NextEvent']):
                # if end_date.date <> now.date;
                result = WaitTime('', sjob['DaysToWait'], sjob['TimeToWater(24h)'], sjob['LastEvent'], jobs['default']['TimeToWater(24h)'], job)
                if result[0] == True:
                    # scheduling watering for set delay
                    # result[1] = seconds to wait, water is func and job is var for Plant ref
                    sc.enter(result[1], 1, water, argument=(job,))
                    
                    print("time to wait; " + str(result[1]) + " for;"  + job)
                elif result[0] == False:
                    continue
            else: 
                # if end_date.date <> now.date;
                result = WaitTime(sjob['NextEvent'],sjob['DaysToWait'], sjob['TimeToWater(24h)'], sjob['LastEvent'], jobs['default']['TimeToWater(24h)'], job)
                if result[0] == True:
                    # scheduling watering for set delay
                    # result[1] = seconds to wait, water is func and job is var for Plant ref
                    sc.enter(result[1], 1, water, argument=(job,)) 





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