# /etc/init.d/puzzlebox.py
### BEGIN INIT INFO
# Provides:          puzzlebox.py
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start daemon at boot time
# Description:       Enable service provided by daemon.
### END INIT INFO

from picamera import PiCamera
import time
import os
import RPi.GPIO as GPIO
from RpiMotorLib import RpiMotorLib
from adafruit_motorkit import MotorKit
from adafruit_motor import stepper


import threading
import sys
import asyncio

#functions
async def arrived(delay, timestamp):
    await capture(timestamp,delay)
    print("departed")
    

async def close_door(delay):
    await asyncio.sleep(delay)
    for x in range(forward_step_number):
        kit.stepper1.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
        time.sleep(0.01)
    print("forward finished")
    time.sleep(0.5)
    for x in range(backward_step_number):
        kit.stepper1.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
        time.sleep(0.01)

    print("forward backwards")
    kit.stepper1.release()
    print("door closed")
    
async def capture(timestamp,delay):
    print("capture started")
    camera.start_recording(capture_dir+"/"+timestamp+".h264",format='h264')
    count = 0
    await close_door(delay)
    while GPIO.input(IR_L_pin) or GPIO.input(IR_R_pin) or count > 50:
        time.sleep(0.3)
        count += 1
    time.sleep(1)
    camera.stop_recording()
    print("capture finnished")
    
    

#objects
user = os.environ["USER"]
camera = PiCamera()
kit = MotorKit()
doorMotor = RpiMotorLib.BYJMotor("TestMotor", "28BYJ")
capture_dir = "/home/"+ user + "/puzzlebox_data/captures"
timeStamp = time.strftime("%a-%d-%m-%y-%H-%M-%S",time.localtime())
log_dir = "/home/" + user + "/puzzlebox_data/log"
IR_L_pin = 21
IR_R_pin = 26

#parameters
door_delay  = 3 #in seconds
forward_step_number = 60
backward_step_number = 55
#objects setups
camera.resolution = (1024,768)
logFileName = log_dir+"/"+"log-file "+timeStamp+".txt"
logFile = open(logFileName,'w')
DM_Pins = [4, 17 ,23, 24]
fullRotation = 512
motor_steps = 50
GPIO.setmode(GPIO.BCM)
GPIO.setup(IR_L_pin,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(IR_R_pin,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

#log file
logFile.write("log session started at "+ timeStamp +"\n")


#test camera
camera.start_preview()
time.sleep(0.5)
save_str = capture_dir +"/"+"cam-test "+timeStamp+".jpg"
camera.capture(save_str)
camera.stop_preview()
logFile.write("camera test finished\n")


#test mototrs
doorMotor.motor_run(DM_Pins,0.001,fullRotation/4,False,False,"half",.001)
time.sleep(0.5)
doorMotor.motor_run(DM_Pins,0.001,fullRotation/4,True, False,"half",.001)
logFile.write("motor test finished\n")


#main loop
try:
    loop = asyncio.get_event_loop()
    print("loop started")
    while True:
        if GPIO.input(IR_R_pin):
            print("right")
            timeStamp = timeStamp = time.strftime("%a-%d-%m-%y-%H-%M-%S",time.localtime())
            logFile.write("opened right " + timeStamp +"\n")
            loop.run_until_complete(arrived(door_delay,timeStamp))
        

        elif GPIO.input(IR_L_pin):
            print("left")
            timeStamp = timeStamp = time.strftime("%a-%d-%m-%y-%H-%M-%S",time.localtime())
            logFile.write("opened left " + timeStamp+"\n")
            loop.run_until_complete(arrived(door_delay,timeStamp))
         
        else:
            pass
except KeyboardInterrupt:
    print("keyboard interrupt caught")
                
#cleanup
    logFile.write("log session closed")
    logFile.close()
    GPIO.cleanup()
        
    

