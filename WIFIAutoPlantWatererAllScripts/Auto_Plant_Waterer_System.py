  #Import libraries for wifi connection for client
import network
import socket
import time
from machine import ADC, Pin, I2C # Allows to use the I2C pins on raspberry pi (GPIO pins 1 and 0)
from ssd1306 import SSD1306_I2C # Allows me to use OLED Display 
from PicoBreadBoard import BUTTON

#GP0=SDA GP1=SCL
# Stores the I2C channel for both displays in use aka the SDA(yellow) and SCL(Blue) pins that are connected, then sets frequency connected to screen
i2c1 = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
i2c2 = I2C(1 , sda=Pin(2), scl=Pin(3), freq=400000)

soil = ADC(Pin(27)) # Soil Moisture Sensor connnected at ADC Pin GP27

BT1 = BUTTON(18) # Button 1 connect at GP18
BT2 = BUTTON(17) # Button 2 connected at GP17
BT3 = BUTTON(16) # Button 3 connected at GP16

relayPin = Pin(13, mode = Pin.OUT) # Relay Pin connected at GP13
relayPin.value(1) # Sets the relayPin value to default the relay to off while in setup

# Object that takes in the dimensions of the screen and then the I2C details from above
display2 = SSD1306_I2C(128, 64, i2c1)
display1 = SSD1306_I2C(128, 64, i2c2)

min_moisture = 10000
max_moisture = 52200

# Sets the default values for these variables
avg_moisture = 0
current_time = 0
checkin = 10
setup = 0

# Wifi name and password to be connected to
ssid = "EagleNet"
password = "}wf*F@9-"

# Initialize Client(Station) mode

wlan = network.WLAN(network.STA_IF) # Set up structure for wifi interface
wlan.disconnect()
wlan.active(False)
wlan.active(True) # Turns on searching for connection/transmitting data
wlan.connect(ssid, password) # Sets up the pico's connection to wifi

max_wait = 10
while max_wait > 0:
    display1.fill(0)
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    display1.text('connecting...', 0, 0)
    display1.show()
    print('waiting for connection...')
    time.sleep(1)
#Handle connection error
if wlan.status() != 3:
    display1.text('connect failed', 0, 0)
    display1.show()
    raise RuntimeError('network connection failed')
else:
    print('connected')
    display1.text('wifi connected', 0, 0)
    display1.show()
    status = wlan.ifconfig()
    print('Server IP: ', status[0])
    
# Set up the client to communicate with the server

addr = socket.getaddrinfo('10.122.138.119', 8080)[0][-1] # Sets up the AP's IP Address and port

try:
    client = socket.socket()
    display1.fill(0)
    display1.text('Connecting', 0, 0)
    display1.text('to server...', 0, 9)
    display1.show()
    print("Attempting to connect to server...")
    client.connect(addr)
    display1.fill(0)
    display1.text('Connection', 0, 0)
    display1.text('Successful!', 0, 9)
    display1.show()
    print("Connected to server.")
    client.send("Hello from Pico W Client!".encode())
    data = client.recv(1024)
    print("Recieved: ", data.decode())
except Exception as e:
    display1.fill(0)
    display1.text('Failed to connect :(', 0, 0)
    display1.show()
    print("Failed to connect: ", e)


display1.fill(0) # Fills screen with black pixels
display2.fill(0)
display1.text("Bryce's Auto", 0, 0)
display1.text("Plant Waterer", 0, 9)
display2.text("Waiting for", 0, 0)
display2.text("plant watering", 0, 18)
display2.text("instructions...", 0, 27)
display1.show()
display2.show()

tooDry = int(client.recv(1024).decode())
print("Recieved: ", tooDry)

finishWater = int(client.recv(1024).decode())
print("Recieved: ", finishWater)

client.close()

while 1:
    current_time += 1 # Sets iterator for check in time
    
    display1.fill(0)
    display2.fill(0) # Fills screen with black pixels
    
    display1.text("Bryce's Auto", 0, 0)
    display1.text("Plant Waterer", 0, 9)
    display1.text("Water will start", 0, 18)
    display1.text("at " + str(tooDry) + " %", 0, 27)
    display1.text("Water will stop", 0, 36)
    display1.text("at " + str(finishWater) + " %", 0, 45)
    
    # read moisture value and convert to percentage into the calibration range
    moisture = (max_moisture - soil.read_u16()) * 100 / (max_moisture - min_moisture) 
    # print moisture and ADC values
    print("moisture: " + "{:.2f}".format(moisture) +"% (adc: "+str(soil.read_u16())+")")
    
    display2.text("Soil Moisture",10,16)
    display2.text(str("{:.2f}".format(moisture)) +" %",35,35)
    
    display1.show()
    display2.show()
    
    avg_moisture += moisture # Adds moisture data to one variable to be averaged every 10 seconds
    
    if current_time == checkin: # If the current time has reached the check in time averages data and decides if it is time to water plant
        if (avg_moisture / checkin) < tooDry: # If the avg moisture reaches below minimum moisture level turns pump on
            relayPin.value(0)
            print("Motor is ON!")
            while moisture < finishWater: # Until moisture level passes maximum water moisture will keep pump on
                moisture = (max_moisture - soil.read_u16()) * 100 / (max_moisture - min_moisture) 
                # print moisture and ADC values and moisture to OLED display
                display2.fill(0)
                display2.text("Soil Moisture",10,16)
                display2.text(str("{:.2f}".format(moisture)) +" %",35,35)
                display2.show()
                print("moisture: " + "{:.2f}".format(moisture) +"% (adc: "+str(soil.read_u16())+")")
                time.sleep(0.1) # delay 100ms
            relayPin.value(1) # When while loop is exited pump turns off
        # Resets these values
        current_time = 0
        avg_moisture = 0
    else :
        relayPin.value(1)
        print("Motor is OFF!")
        
    
        
        
    time.sleep(1) # delay 1s
   