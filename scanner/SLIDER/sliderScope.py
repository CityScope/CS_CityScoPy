# ! /usr/bin/python

#Cooper Hewitt Mech-Slider : Carson Smuts 
#
#A simple class to connect and read the mechanical slider.
#All computation, control and encoding is done on the slider hardware.
#This simple open a USB port to the hardware and listens to messages coming through.
#
#
#

import sys
import glob
import time

import serial
from serial import SerialException

import socket

from threading import Thread

UDP_IP = "127.0.0.1"
UDP_PORT = 7777
sliderScopeAddress = '/dev/tty.usbmodem11'
sliderScopePort = serial.Serial()

enableUDP = False

sliderValue = "-1"



class sliderObject(object):

    def __init__(self):

        try:
            global sliderScopePort
            sliderScopePort = serial.Serial(sliderScopeAddress, 115200)
            #thread = Thread(target=self.sliderT, args=())
            #thread.daemon = True  # Daemonize
            #thread.start()
        except SerialException:
            print ('Could not start SliderScope.... port already open.... or not found.... check with Carson')

    def sliderT(self):
        while True:
            print ("Testing Threads") #too slow for UI purposes.......

    def sliderRunner(self):
        #while True:
        global sliderValue
        #print "running"
        #print (sliderValue)
        try:
            sliderScopePort.reset_input_buffer()
            # sliderScopePort.flush()
            #time.sleep(.1)
            x = sliderScopePort.readline()

            if x:
                sliderValue = x
                if (enableUDP):
                    sock = socket.socket(socket.AF_INET,  # Internet
                    socket.SOCK_DGRAM)  # UDP
                    sock.sendto(x, (UDP_IP, UDP_PORT))


        except SerialException:
            print ('SliderScope unavailable.... check with Carson')
            sliderValue = "-1"



    #Do NOT use this function..... for testing only
def serial_ports():
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result



