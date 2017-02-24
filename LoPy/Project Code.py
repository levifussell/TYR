# Project Code

# Ultrasonic Sensor
# This sensor has 4 pins, VCC, GND, TRIGGER and ECHO.
# Connect:
# - VCC to VIN on the expansion board. (This only works well when the sensor is powered by 5V, so power the expansion board from the USB port).
# - GND to GND on the expansion board.
# - TRIGGER to any output pin on the LoPy (e.g. P11).
# - ECHO to any input pin on the LoPy (e.g. P12), via a resistor divider. Use for instance a 10K and a 20K resistor divider to take the 5V output of the sensor to a safe 3V3 for the LoPy.

# Ultrasonic sensor interface

from machine import Pin
import time
import machine

# LoPy test OTAA
# UoE LoRaWAN based on TTN v2 back-end

from network import LoRa
import socket
import binascii
import pycom

# SD Card Writing

from machine import SD
import os

# Separate thread for posting to web

from machine import Timer


# this class is used to setup and interface with an ultrasonic sensor
# distance function has been reworked to respond true when distance of the object
# in front within the MAX_DIST threshold and false if the object is outside that range
class HCSR04:
    def __init__(self, trigger, echo):
        # Anything over 400 cm (23200 us pulse) is "out of range"
        self.MAX_DIST = 23200
        self._trigger = Pin(trigger, mode=Pin.OUT, value=0)
        self._echo = Pin(echo, mode=Pin.IN)
	
	# call to see if person is within threshold distance of sensor
    def distance(self):
        # Hold the trigger pin high for at least 10 us
        self._trigger(1)
        time.sleep_us(11)
        self._trigger(0)

        # Wait for pulse on echo pin
        while not self._echo():
            machine.idle()

        # Measure how long the echo pin was held high (pulse width)
        # Note: the micros() counter will overflow after ~70 min
        t1 = time.ticks_us()
        while self._echo():
            pass
        t2 = time.ticks_us()
        pulse_width = t2 - t1

        # Calculate distance in centimeters. The constants are found
        # in the datasheet, and calculated from the assumed speed
        # of sound in air at sea level (~340 m/s).
        # cm = pulse_width / 58.0;
        # this calculation is not needed

        # return the results
        if pulse_width > self.MAX_DIST:
            return False
        else:
            return True


# Pass counter object setup for sensor used to record when a pass is completed from the right or left and
# the time spent in front of the sensor. Records are made in a CSV file stored in the root directory of an SD card 
# present in the device. Also includes functionality to send the contents of the data file over the network or delete
# the contents from the filing system. Can chose to send only data 
class Pass_Count:
    def __init__(self, ident):
    	# only six sensors registered check the setup identifier is one of these
        if 1 > int(ident) or 6 < int(ident):
            # Turn off hearbeat LED
            pycom.heartbeat(False)
            # make string of ID number
            self.ident = str(ident)
            # set filename to given door name
            self.name = 'path_' + self.ident
            # create sd card object
            sd = SD()
            # mount the sd card
            os.mount(sd, '/sd')
            # open filename for given door
            self.f = open('/sd/' + self.name + '.txt', 'w')
            # write the csv file head
            self.f.write('Timecode,Sensor_ID,Time_Stopped,Right_Pass,Left_Pass')
            # write first data entry starting timecode identifer 
            self.f.write(str(time.time()) + ',' + self.ident + '0,0,0')
        else:
            print("That's not a valid option! Only 6 sensors!")
            
    # call this when person has passed sensor from right
    def right(self, count):
        # write timecode, time in front of sensors, set right pass value to 1, and set left pass value to 0
        self.f.write(
            "{0},{1},{2},{3},{4}".format(str(time.time()), self.ident, str(count), str(1), str(0)))
            
    # call this when person has passed sensor from left
    def left(self, count):
        # write timecode, time in front of sensors, set right pass value to 0, and set left pass value to 1
        self.f.write(
            "{0},{1},{2},{3},{4}".format(str(time.time()), self.ident, str(count), str(0), str(1)))
	
	# call this to send file over the network
	# sends the entire content of CSV file
    def send_file(self):
        # setup the networking
        nw = Lora_Network(self.ident)
        # close file if open
        self.f.close()
        # open file for reading
        with open('/sd/' + self.name + '.txt', 'r') as f:
            # read a line
            for line in f:
                # convert line in bytes
                data_bytes = bytes(str(line), 'utf-8')
                # make the socket blocking
                # (waits for the data to be sent and for the 2 receive windows to expire)
                nw.s.setblocking(True)
                # send some data
                nw.s.send(data_bytes)
                # make the socket non-blocking
                # (because if there's no data received it will block forever...)
                nw.s.setblocking(False)
    	# close the network connection
    	nw.diconnect()
        # close the file
        f.close()
    
    # call this to send the data contained in rows of the 
    # CSV file in which time measured for pass is greater
    # than the lower bound provided.
    def send_time_greater(self, lower_bound):
        # setup the networking
        nw = Lora_Network(self.ident)
        # close file if open
        self.f.close()
        # open file for reading
        with open('/sd/' + self.name + '.txt', 'r') as f:
            # read a line
            for line in f:
            	if line.split(',')[1] > lower_bound:
                    # convert data in bytes
                    data_bytes = bytes(str(line), 'utf-8')
                    # make the socket blocking
                    # (waits for the data to be sent and for the 2 receive windows to expire)
                    nw.s.setblocking(True)
                    # send some data
                    nw.s.send(data_bytes)
                    # make the socket non-blocking
                    # (because if there's no data received it will block forever...)
                    nw.s.setblocking(False)
            # close the network connection
            nw.diconnect()
            # close the file
            f.close()
            
    # call this to send the data contained in rows of the 
    # CSV file in which time measured for pass is lower
    # than the upper bound provided.
    def send_time_lower(self, upper_bound):
        # setup the networking
        nw = Lora_Network(self.ident)
        # close file if open
        self.f.close()
        # open file for reading
        with open('/sd/' + self.name + '.txt', 'r') as f:
            # read a line
            for line in f:
            	if line.split(',')[1] < upper_bound:
                	# convert data in bytes
                	data_bytes = bytes(str(line), 'utf-8')
                	# make the socket blocking
                	# (waits for the data to be sent and for the 2 receive windows to expire)
                	nw.s.setblocking(True)
                	# send some data
                	nw.s.send(data_bytes)
                	# make the socket non-blocking
                	# (because if there's no data received it will block forever...)
                	nw.s.setblocking(False)
    		# close the network connection
    		nw.diconnect()
        	# close the file
        	f.close()
    
    # call this to send the data contained in rows of the 
    # CSV file in which time measured for pass is lower
    # than the upper bound and greater than the lower bound.
    def send_time_between(self, lower_bound, upper_bound):
        # setup the networking
        nw = Lora_Network(self.ident)
        # close file if open
        self.f.close()
        # open file for reading
        with open('/sd/' + self.name + '.txt', 'r') as f:
            # read a line
            for line in f:
            	if line.split(',')[1] > lower_bound and line.split(',')[1] < upper_bound:
                	# convert data in bytes
                	data_bytes = bytes(str(line), 'utf-8')
                	# make the socket blocking
                	# (waits for the data to be sent and for the 2 receive windows to expire)
                	nw.s.setblocking(True)
                	# send some data
                	nw.s.send(data_bytes)
                	# make the socket non-blocking
                	# (because if there's no data received it will block forever...)
                	nw.s.setblocking(False)
    		# close the network connection
    		nw.diconnect()
        	# close the file
        	f.close()
    
    # call this to wipe all data stored in the CSV file
    # use this function after transferring the desired data
    # from the contents of the file.
    def wipe_data(self):
		# close file if open
        self.f.close()
        # delete the file
        os.remove('/sd/' + self.name + '.txt')
        # open new file by the same name
        self.f = open('/sd/' + self.name + '.txt', 'w')
        # write the csv file head
        self.f.write('Timecode,Sensor_ID,Time_Stopped,Right_Pass,Left_Pass')
	
	# close file upon destruction of object
    def __del__(self):
        # close file on exiton exit
        self.f.close()


# network interface used to connect to Lora Network
class Lora_Network:
    def __init__(self, ident):
        if 1 > int(ident) or 6 < int(ident):
            # ID Switcher based on board number
            # Six boards have been configured for use on the project
            if ident == 1:
                # Board 1 Identification Strings
                AppEUI = '70 B3 D5 7E F0 00 3A 56'
                AppID = 'team_dallas'
                AppKey = 'B9 51 88 C7 6D A9 25 17 57 37 E6 31 DD 32 A8 D4'
                DevEUI = '70 B3 D5 49 93 EC 3A B8'
                DevID = 'teamd1'

            elif ident == 2:
            	# Board 2 Identification Strings
            	AppEUI = '70 B3 D5 7E F0 00 3A 56'
            	AppID = 'team_dallas'
            	AppKey = '90 35 EF A3 C0 42 69 3B F0 D5 02 28 CB D3 DB 24'
            	DevEUI = '70 B3 D5 49 94 D3 E6 0E'
            	DevID = 'teamd2'

            elif self.ident == 3:
            	# Board 3 Identification Strings
            	AppEUI = '70 B3 D5 7E F0 00 3A 56'
            	AppID = 'team_dallas'
            	AppKey = '2F 47 1F 8F 0C AE 19 A1 1A 5B 23 23 63 38 E7 17'
            	DevEUI = '70 B3 D5 49 9F 9C FC 56'
            	DevID = 'teamd3'

            elif self.ident == 4:
            	# Board 4 Identification Strings
            	AppEUI = '70 B3 D5 7E F0 00 3A 56'
            	AppID = 'team_dallas'
            	AppKey = '01 36 11 39 E6 6A D6 99 91 B9 62 36 B9 7C 07 EE'
            	DevEUI = '70 B3 D5 49 9C FF C1 3E'
            	DevID = 'teamd4'

            elif self.ident == 5:
            	# Board 5 Identification Strings
            	AppEUI = '70 B3 D5 7E F0 00 3A 56'
            	AppID = 'team_dallas'
            	AppKey = 'F5 5D AF 7A 0E 87 07 37 77 B4 7B 4A D5 FA B1 8D'
            	DevEUI = '70 B3 D5 49 9F B0 EA E0'
            	DevID = 'teamd5'

            else:
                # Board 6 Identification Strings
                AppEUI = '70 B3 D5 7E F0 00 3A 56'
                AppID = 'team_dallas'
                AppKey = 'BB 93 34 AE 9B FB 8E D5 E3 07 21 7C 63 11 FE 8C'
                DevEUI = '70 B3 D5 49 98 C7 B3 68'
                DevID = 'teamd6'
            try:
                # Initialize LoRa in LORAWAN mode.
                lora = LoRa(mode=LoRa.LORAWAN)
                # create an OTAA authentication parameters
                app_eui = binascii.unhexlify(AppEUI.replace(' ', ''))
                app_key = binascii.unhexlify(AppKey.replace(' ', ''))
                # join a network using OTAA (Over the Air Activation)
                lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0)
                # wait until the module has joined the network
                while not lora.has_joined():
                    time.sleep(10)
                    print('Not yet joined...')
                # successfully joined the network
                print('Joined Network')
                # create a LoRa socket
                self.s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
                # set the LoRaWAN data rate
                self.s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)
                # print connection sucess
                print (AppID + '-' +DevEUI + '-' + DevID + ' connected')
            except:
                print("Error Connecting to Network!!")
        else:
            print("That's not a valid option! Only 6 network adapters!")
	
	# call to close socket connection with server
    def disconnect(self):
        # close network connection
        self.s.socket.close()
	
	# close network connection upon destruction of object
    def __del__(self):
        # close network connection
        self.s.socket.close()


# Create this object to detect the number of passes using the specific board
# configuration with two ultrasonic sensors. Initialization is done by declaring
# the sensor ID and the echo and trigger pins for the two ultrasonic sensors 
class Pass_Detect:
    def __init__(self, IDENT, TRIGGER_1, ECHO_1, TRIGGER_2, ECHO_2):
        # Green Color
        self.green = 0x003300
        # Blue Color
        self.blue = 0x000033
        # White Color
        self.white = 0x7f7f7f
        # setup the first ultrasonic sensor
        self.hc_1 = HCSR04(TRIGGER_1, ECHO_1)
        # setup the second ultrasonic sensor
        self.hc_2 = HCSR04(TRIGGER_2, ECHO_2)
        # setup pass counter
        self.pc = Pass_Count(IDENT)
        # initialize the timer
        self.chrono = Timer.Chrono()
        # set light to white
        pycom.rgbled(self.white)

	# Use two ultrasonic sensor and determine which sensor gets activated first and based 
	# on that value you can determine from what size people have passes. A timer is also
	# used starting from when an object is first detested to when it is no longer in view 
	# from either of the sensors.
    def detect_pass(self):
    	# continue to poll for data as quickly as possible
    	# could include a time delay to give certain interval for
    	# testing the distance calculation
        while True:
            # left sensor detect distance first
            if self.hc_1.distance():
                # start timer
                self.chrono.start()
                # check if subject in view from either distance sensors
                while self.h_1.distance() or self.h_2.distance():
                    # set light to green shows person is still in view 
                    # and the person has approached from the left
                    pycom.rgbled(self.green)
                # stop the timer
                self.chrono.stop()
                # get the time passed since detection
                elapsed_time = int(self.chrono.read())
                # record the time present and pass
                self.pc.left(elapsed_time)
                # reset the timer
                self.chrono.reset()
                # set light to white
                pycom.rgbled(self.white)
            # right sensor detects distance first
            elif self.hc_2.distance():
                # start timer
                self.chrono.start()
                # check if subject in view from either distance sensors
                while self.h_1.distance() or self.h_2.distance():
                    # set light to blue shows person is still in view 
                    # and the person has approached from the right
                    pycom.rgbled(self.blue)
                # stop the timer
                self.chrono.stop()
                # get the time passed since detection
                elapsed_time = int(self.chrono.read())
                # record the time present and pass
                self.pc.right(elapsed_time)
                # reset the timer
                self.chrono.reset()
                # set light to white
                pycom.rgbled(self.white)

	# send all the data stored on card
    def send_data(self):
        self.pc.send_data(self)

	# send all data for waiting values greater than the lower bound
	def send_gt(self,lower_bound):
		self.pc.send_data(self,lower_bound)
	
	# send all data for waiting values less than the upper bound
	def send_lt(self,upper_bound):
		self.pc.send_data(self,upper_bound)
	
	# send all data for waiting values between the the lower bound and upper bound
	def send_btw(self,lower_bound, upper_bound):
		self.pc.send_data(self,lower_bound,upper_bound)
	
	# delete all data stored on card
	def delete_data(self):
		self.pc.wipe_data(self)
	
			
######## Here is the api for project #########
## Example Code used for board applications ##
# Creates the pass detector for board 1
# 'P11','P12' are on the left
# 'P10','P13' are on the right
## PD = Pass_Detect(1, 'P11', 'P12', 'P10', 'P13')

# Determine the number of people passing by using two ultrasonic sensors
# Run continuously and records the timestamp, pass id, 
# time stopped, number of passes on right, and number of passes on left
## PD.detect_pass()

# Send all data stored on card
## PD.send_data()

# sends all data with wait times greater than 5 seconds
## PD.send_gt(5)

# sends all data with wait times less than 5 seconds
## PD.send_lt(5)

# sends all data with wait times between 5 seconds and 10 seconds
## PD.send_btw(5,10)

# Deletes all data stored on the card
## PD.delete_data()

### TODO ###
# Allow board to board communication for transferring data amongst themselves to increase range
# with away from the receiver in which device can function
# Allow requests before, after, and between timecodes
# Give option for on device analytics including number of people passing on left/right/total
# Connect with Make mockup gui including options to switch or add Sensor IDs, find Passes Left/Right/Total
# Specify ranges of wait times and events between calendar dates, Transmit Data, and Clear Memory