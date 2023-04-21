import bluetooth
import pygame
import random
import time
from hx711 import HX711
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM) 

host = ""
port = 1
makeDrink = True

pump1 = 17
pump2 = 18
pump3 = 27
pump4 = 22
pump5 = 26
afstandSensor1Trig = 6
afstandSensor1Echo = 13
afstandSensor2Trig = 23
afstandSensor2Echo = 24
weightDT = 25
weightSCK = 12
ledGreen1 = 10
ledGreen2 = 9
ledGreen3 = 11
ledYellow1 = 4
ledYellow2 = 8
ledYellow3 = 7
ledRed1 = 16
ledRed2 = 20
ledRed3 = 21

calibrationFactor = -557.3
weightOfRist = 95810 #79100

GPIO.setup(pump1, GPIO.OUT)  
GPIO.setup(pump2, GPIO.OUT)  
GPIO.setup(pump3, GPIO.OUT)  
GPIO.setup(pump4, GPIO.OUT)  
GPIO.setup(pump5, GPIO.OUT)  
GPIO.setup(afstandSensor1Trig, GPIO.OUT)
GPIO.setup(afstandSensor2Trig, GPIO.OUT)
GPIO.setup(afstandSensor1Echo, GPIO.IN)
GPIO.setup(afstandSensor2Echo, GPIO.IN)
GPIO.setup(weightDT, GPIO.IN)
GPIO.setup(weightSCK, GPIO.IN)
GPIO.setup(ledGreen1, GPIO.OUT)
GPIO.setup(ledGreen2, GPIO.OUT) 
GPIO.setup(ledGreen3, GPIO.OUT) 
GPIO.setup(ledYellow1, GPIO.OUT)
GPIO.setup(ledYellow2, GPIO.OUT) 
GPIO.setup(ledYellow3, GPIO.OUT) 
GPIO.setup(ledRed1, GPIO.OUT)
GPIO.setup(ledRed2, GPIO.OUT) 
GPIO.setup(ledRed3, GPIO.OUT) 

typeDrink = 0

file = open("virk.txt","w")

#Opretter vægtsensor klassen
weightSensor = HX711(dout_pin=weightDT, pd_sck_pin = weightSCK, gain = 64)
weightSensor.reset()

def readDistance(echo, trig):
    #Denne funktion skal kaldes når glasset er placeret
    GPIO.output(trig,True)
    time.sleep(0.00001)
    GPIO.output(trig,False)
    
    startTime = time.time()
    stop = time.time()
    
    while not GPIO.input(echo):
        #Dette er for at sikre at den ikke kommer til at sidde fast i dette loop
        if startTime-stop > 0.5:
            #startTime = time.time()
            return 10
        
        #Vent på at den bliver lav
        startTime = time.time()
        
    
    while GPIO.input(echo):
        stop = time.time()
    
    tid = (stop-startTime)
    distance = tid*17000
    print("Dist: ", distance, " Echo: ",echo)
    if distance is None:
        print("none")
    return abs(distance)


def getWeight():
    weight = (sum(weightSensor.get_raw_data(2))/2+weightOfRist) / calibrationFactor

    return weight


def startPump(pumpNR):
    if pumpNR == 1:
        GPIO.output(pump1, True)
    elif pumpNR == 2:
        GPIO.output(pump2, True)
    elif pumpNR == 3:
        GPIO.output(pump3, True)
    elif pumpNR == 4:
        GPIO.output(pump4, True)
    else:
        GPIO.output(pump5, True)
    
    return

def stopPump(pumpNR):
    if pumpNR == 1:
        GPIO.output(pump1, False)
    elif pumpNR == 2:
        GPIO.output(pump2, False)
    elif pumpNR == 3:
        GPIO.output(pump3, False)
    elif pumpNR == 4:
        GPIO.output(pump4, False)
    else:
        GPIO.output(pump5, False)
    return

def makeDrinkMulti(drink):
    #Denne funktion hælder væskerne samtidig
    #Venter på at glasset står på vægten
    #while getWeight() < 30:
        #Evt. lille advarsel/notifikation
        #continue
    turnOffLed()
    
    #Læser afstandssensor
    while readDistance(afstandSensor1Echo,afstandSensor1Trig) > 4 or readDistance(afstandSensor2Echo,afstandSensor2Trig) > 4:
        #Evt. lav en lille advarsel til brugeren
        GPIO.output(ledRed1,True)
        GPIO.output(ledRed2,True)
        GPIO.output(ledRed3,True)
        print("Ting")
        continue

    turnOffLed()
    
    file.write("I makeDrink funktion")
    
    print("her")
    activePumpList = [0,0,0,0,0] 
    weightList = [0,0,0,0,0]
    oldWeight = getWeight() #Var 0 før, men er ret sikker på at dette burde virke
    
    for i,liquid in enumerate(drink):
        if liquid > 0:
            startPump(i+1)
            activePumpList[i] = 1
    
    while True:
        activePumps = sum(activePumpList)
        
        if activePumps == 0:
            break
        
        weight = getWeight()
        
        print(weight)
        #print(weightList)
        print(activePumpList)
        
        for i,liquid in enumerate(drink):
            #Dette er for at sikre at den ikke stoper ved en fejlmåling
            if weight > 250:
                break
            
            if 0 < liquid - weightList[i]:
                weightList[i] += (weight-oldWeight)/activePumps
            else:
                stopPump(i+1)
                activePumpList[i] = 0
                
            progressBar(sum(weightList),sum(drink))
            
        if weight < 250:        
            oldWeight = weight
        #print(weightList)
    print("done")
    print(typeDrink)
    
    file.write("I makeDrink 2")
    
    
    pygame.mixer.music.stop()
    if typeDrink == 1:
        client.send("loading1")
    if typeDrink == 2:
        client.send("loading2")
    file.write("slut makeDrink")
    stop()
    return True

def progressBar(currentWeight, totalWeight):
    percent = currentWeight/totalWeight*100
    
    if percent >= 11:
        GPIO.output(ledRed1,True)
        
    if percent >= 22:
        GPIO.output(ledRed2,True)
    
    if percent >= 33:
        GPIO.output(ledRed3,True)
        
    if percent >= 44:
        GPIO.output(ledYellow1,True)
    
    if percent >= 55:
        GPIO.output(ledYellow2,True)
    
    if percent >= 66:
        GPIO.output(ledYellow3,True)
        
    if percent >= 77:
        GPIO.output(ledGreen1,True)
    
    if percent >= 88:
        GPIO.output(ledGreen2,True)
    
    if percent >= 100:
        GPIO.output(ledGreen3,True)
        

def turnOffLed():
    GPIO.output(ledRed1,False)
    GPIO.output(ledRed2,False)
    GPIO.output(ledRed3,False)
    GPIO.output(ledYellow1,False)
    GPIO.output(ledYellow2,False)
    GPIO.output(ledYellow3,False)
    GPIO.output(ledGreen1,False)
    GPIO.output(ledGreen2,False)
    GPIO.output(ledGreen3,False)

def turnOnLed():
    GPIO.output(ledRed1,True)
    GPIO.output(ledRed2,True)
    GPIO.output(ledRed3,True)
    GPIO.output(ledYellow1,True)
    GPIO.output(ledYellow2,True)
    GPIO.output(ledYellow3,True)
    GPIO.output(ledGreen1,True)
    GPIO.output(ledGreen2,True)
    GPIO.output(ledGreen3,True)

def stop():
    file.write("Start i stop funktion")
    pygame.mixer.init()
    pygame.mixer.music.load("stop.mp3")
    pygame.mixer.music.play()
    time.sleep(2)
    file.write("Slut i stop")
    
server = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
print('Bluetooth Socket Created')
try:
        server.bind((host, port))
        print("Bluetooth Binding Completed")
        pygame.mixer.init()
        pygame.mixer.music.load("pair.mp3")
        pygame.mixer.music.play()
        time.sleep(4)
        pygame.mixer.init()
        pygame.mixer.music.load("elevator.mp3")
        pygame.mixer.music.play()
except:
        print("Bluetooth Binding Failed")
server.listen(1)

client, address = server.accept()
print("Connected To", address)
print("Client:", client)
pygame.mixer.music.stop()
pygame.mixer.init()
pygame.mixer.music.load("succ.mp3")
pygame.mixer.music.play()
play = False

try:
        while True:
                data = client.recv(1024).decode()
                print(data)
                
                #Dette er til at lave drink
                dataToList = data.split(":")
                
                print(dataToList)
                #Der sendes et 1 hvis der skal laves en drink
                if makeDrink:
                    if dataToList[0] == "1":
                        typeDrink = 1
                    if dataToList[0] == "2":
                        typeDrink = 2
                    makeDrink = False
                    l1 = int(dataToList[1])
                    l2 = int(dataToList[2])
                    l3 = int(dataToList[3])
                    l4 = int(dataToList[4])
                    l5 = int(dataToList[5])
                    
                    pygame.mixer.init()
                    randomNummer = random.randint(1, 5)
                    pygame.mixer.music.load(str(randomNummer) + ".mp3")
                    pygame.mixer.music.play()
                        
                    makeDrinkMulti([l1,l2,l3,l4,l5])
                    makeDrink = True
                    pygame.mixer.music.stop()
                    
                
                if "test" in str(data):
                    if play == False:
                        play = True
                        print("play")
                    else:
                        pygame.mixer.music.stop()
                        play = False
                         
                # Sending the data.
                #client.send(send_data)
except Exception as error:
        print("Except")
        file.write("\n")
        file.write(str(error))
        file.close()
        # Making all the output pins LOW
        GPIO.cleanup()
        stopPump(1)
        stopPump(2)
        stopPump(3)
        stopPump(4)
        stopPump(5)
        # Closing the client and server connection
        client.close()
        server.close()
