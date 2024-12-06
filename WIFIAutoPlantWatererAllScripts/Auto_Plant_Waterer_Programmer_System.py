#import libraries for wifi connection
import network
import socket
import time
from machine import Pin, I2C # Allows to use the I2C pins on raspberry pi (GPIO pins 1 and 0)
from ssd1306 import SSD1306_I2C # Allows me to use OLED Display 
from PicoBreadboard import BUTTON

#GP0=SDA GP1=SCL
# Stores the I2C channel for both displays in use aka the SDA(yellow) and SCL(Blue) pins that are connected, then sets frequency connected to screen
i2c1 = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
i2c2 = I2C(1 , sda=Pin(2), scl=Pin(3), freq=400000)

BT1 = BUTTON(18) # Button 1 connect at GP18
BT2 = BUTTON(17) # Button 2 connected at GP17
BT3 = BUTTON(16) # Button 3 connected at GP16

# Object that takes in the dimensions of the screen and then the I2C details from above
display2 = SSD1306_I2C(128, 64, i2c1)
display1 = SSD1306_I2C(128, 64, i2c2)

# When program starts restarts screen to blank
display1.fill(0)
display2.fill(0)

min_moisture = 10000
max_moisture = 52200

# Sets the default values for these variables
avg_moisture = 0
current_time = 0
checkin = 10
tooDry = 0
finishWater = 0
setup = 0

#This is the code for the AP(Access-Point) so other clients/stations(plant waterers) to connect into and get their instructions from

display1.text('Attempting to EagleNet Wifi', 0, 0)
display1.show()

# Wifi name and password to be connected to
ssid = "EagleNet"
password = "}wf*F@9-"

wlan = network.WLAN(network.STA_IF) #Sets up the structure for the wifi interface
wlan.active(True)
wlan.connect(ssid, password)

max_wait = 10
while max_wait > 0:
    display1.fill(0) # Clear display for wifi connection
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    display1.text('connecting...', 0, 0)
    display1.show()
    print('waiting for connection...')
    time.sleep(1)
    print(max_wait)
# Handle connection error
if wlan.status() != 3:
    display1.text('connect failed', 0, 0)
    display1.show()
    raise RuntimeError('network connection failed')
else:
    print('connected')
    display1.text('connected', 0, 0)
    display1.show()
    status = wlan.ifconfig()
    print('Server IP: ', status[0])
    
#Below is the setup code for the server on the AP

addr = socket.getaddrinfo('0.0.0.0', 8080)[0][-1] # Allows server to listen for incoming conections

server = socket.socket() # Allows device to send and recieve data over a network.
server.bind(addr) # Associates the socket with the neccessary network interface and port number on the device
server.listen(5) #Changes  the socket from connecting to listening with a maximum of one queued connection

print("Server listening on ", addr)

display1.fill(0)
display1.text('Attempting to ', 0, 0)
display1.text('connect to', 0, 9)
display1.text('Auto Plant Waterer', 0, 18)
display1.show()


conn, client_addr = server.accept() # Waits for a client to connect to the server and gets its socket object and tuple containing its IP and port
print("Client connected from: ", client_addr) # Let User know connection to the client was successful
display1.fill(0)
display1.text('Successfully connected', 0, 0)
display1.text('to Auto Plant Waterer', 0, 9)
display1.show()
    
data = conn.recv(1024) # Allows server to recieve up to 1024 bytes of data
print("Recieved: ", data.decode()) # Shows user the data that was recieved

conn.send("Hello from Pico W AP!".encode()) # Sends data back out to client


while setup != 2:
    display1.fill(0) # Fills screen with black pixels
    display2.fill(0)
    
    display1.text("Bryce's Auto", 0, 0)
    display1.text("Plant Waterer", 0, 9)
    if setup == 0:
        display1.text("Set start water", 0, 18)
        display1.text("moisture level", 0, 27)
    else :
        display1.text("Set finish water", 0, 18)
        display1.text("moisture level", 0, 27)
    display1.text("BT3 to continue", 0, 45)
    display2.text("BT1 raises level", 0, 0)
    display2.text("BT2 lowers level", 0, 9)
    if setup == 0:
        display2.text("Moisture: " + str(tooDry) + " %", 14, 35)
    else :
        display2.text("Moisture: " + str(finishWater) + " %", 14, 35)
    display1.show()
    display2.show()
    
    # Checks and runs program depending on which button is pressed
    if BT1.read() == 1: # If button 1 is pressed increases moisture level to start watering
        if setup == 0:
            tooDry += 1
        else :
            finishWater += 1
    elif BT2.read() == 1: # If button 2 is pressed decreases moisture level to start watering
        if setup == 0:
            if tooDry != 0:
                tooDry -= 1
        else :
            finishWater -= 1
    elif BT3.read() == 1: # When BT3 pressed continues through setup until setup == 2 finishes setup and kicks out of current loop
        setup += 1
    
    # Prints to console to show the current tooDry variable value
    print(tooDry)
    print(finishWater)
    
    time.sleep(0.25) # Delay set to 250ms

# Data sent in string format bc ints cant be converted to byte format to be transfered 
conn.send(str(tooDry).encode()) # Sends data back out to client
conn.send(str(finishWater).encode()) 

conn.close() # Closes connection

# Clears the setup display
display1.fill(0) 
display2.fill(0)
    
# Default display for after plant waterer has been programmed
display1.text("Bryce's Auto", 0, 0)
display1.text("Plant Waterer", 0, 9)
display1.text("has been", 0, 18)
display1.text("succesfully", 0, 27)
display1.text("programmed!", 0, 36)
display2.text(":D", 35,35)
display1.show()
display2.show()


    
    
    
    
    
    
    