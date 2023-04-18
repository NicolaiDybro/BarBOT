import bluetooth
import pygame
import time

import RPi.GPIO as GPIO
led_pin = 4    
GPIO.setmode(GPIO.BCM)  
GPIO.setup(led_pin, GPIO.OUT)  
host = ""
port = 1

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
                data = client.recv(1024)
                print(data)
                
                #Dette er til at lave drink
                dataToList = data.split(":")
                print("Her")
                print(dataToList)
                #Der sendes et 1 hvis der skal laves en drink
                if dataToList[0] == "1":
                    #MakeDrinkMulti med de resterende 5 værdier
                    continue
                
                if "test" in str(data):
                    if play == False:
                        play = True
                        print("play")
                        pygame.mixer.init()
                        pygame.mixer.music.load("teq.mp3")
                        pygame.mixer.music.play()
                    else:
                         pygame.mixer.music.stop()
                         play = False
                         
                if data == "1":
                        GPIO.output(led_pin, True)
                        send_data = "Light On "
                elif data == "0":
                        GPIO.output(led_pin, False)
                        send_data = "Light Off "
                else:
                        send_data = "Type 1 or 0 "
                # Sending the data.
                client.send(send_data)
except:
        # Making all the output pins LOW
        GPIO.cleanup()
        # Closing the client and server connection
        client.close()
        server.close()
