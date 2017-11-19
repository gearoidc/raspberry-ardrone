#!/usr/bin/env python

import RPi.GPIO as GPIO
import libardrone
import LCD1602
import PCF8591 as ADC
import time
import math

TRIG = 11
ECHO = 12
MAX_HEIGHT = 1500
MAX_HAND_DISTANCE = 100

def setup():
  global state
  global drone
  global running
  global flying
  global battery_level

  LCD1602.init(0x27, 1)   # init(slave address, background light)
  LCD1602.write(0, 0, 'Greeting!!')
  LCD1602.write(1, 1, 'Coderdojo:-)')

  ADC.setup(0x48)                                 # Setup PCF8591

  GPIO.setmode(GPIO.BOARD)
  GPIO.setup(TRIG, GPIO.OUT)
  GPIO.setup(ECHO, GPIO.IN)
  drone = libardrone.ARDrone()
  drone.set_speed(0.2)

def showDirect(direction):
  LCD1602.clear()
  LCD1602.write(0, 0, 'AR Drone Demo!!')
  LCD1602.write(1, 1, direction)

def loop():
  running = True
  flying = False
  status = '';
  current_dist = distance()
  dis = -1
  alt = 0

  while running:
    try:

      d = direction()
      if flying:
        dis = distance()
        battery_level = drone.navdata.get(0, dict()).get("battery", 0)

      if d == 'home':
        if flying:
          drone.hover()
        status = d
      elif d == 'pressed':
        flying = False
        running = False
      elif d == 'up':
        if flying == False:
          flying = True
          drone.takeoff()

        if flying:
          drone.move_up()
        dis = 0
      elif d == 'down':
        drone.move_down()
        dis = 0
      elif d == 'left':
        drone.move_left()
      elif d == 'right':
        drone.move_right()
      else:
        print drone.navdata.get(0, dict()).get("battery", 0)

      if flying and dis > 0 and dis <= MAX_HAND_DISTANCE and current_dist > 0 and current_dist <= MAX_HAND_DISTANCE:
        if dis <= MAX_HAND_DISTANCE:
          if dis > current_dist:
            alt = drone.navdata.get(0, dict()).get("altitude", 0)
            print 'drone up', dis, current_dist, alt, battery_level
            drone.move_up()
            showDirect('up %d %d' %(dis, alt))
          elif dis < current_dist:
            alt = drone.navdata.get(0, dict()).get("altitude", 0)
            print 'drone down', dis, current_dist, alt, battery_level
            drone.move_down()
            showDirect('down %d %d' %(dis, alt))

      if status != '' and status != d:
        showDirect(d)
      status = d
      current_dist = dis

      if flying:
        alt = drone.navdata.get(0, dict()).get("altitude", 0)
        vx = drone.navdata.get(0, dict()).get("vx", 0)
        vy = drone.navdata.get(0, dict()).get("vy", 0)

      if alt > MAX_HEIGHT:
        drone.land()
        flying = False
        running = False

      if flying and drone.navdata.get(0, dict()).get("battery", 0) < 30:
        drone.land()
        print "Battery too low landin, Please change" 
        running = False
      time.sleep(0.15)
    except:
      pass

  print "Shutting down...",
  print "Battery ", drone.navdata.get(0, dict()).get("battery", 0)
  drone.land()
  drone.halt()
  GPIO.cleanup()
  showDirect('landed')
  print "Ok."

def destroy():
  drone.land()
  drone.reset()
  GPIO.cleanup()

def distance():
  GPIO.output(TRIG, 0)
  time.sleep(0.000002)

  GPIO.output(TRIG, 1)
  time.sleep(0.00001)
  GPIO.output(TRIG, 0)

  while GPIO.input(ECHO) == 0:
    a = 0
  time1 = time.time()
  while GPIO.input(ECHO) == 1:
    a = 1
  time2 = time.time()

  during = time2 - time1
  return math.ceil(during * 340 / 2 * 100)

def direction():        #get joystick result
  state = ['home', 'up', 'down', 'left', 'right', 'pressed']
  i = 0

  if ADC.read(0) <= 5:
    i = 1           #up

  if ADC.read(0) >= 250:
    i = 2           #down

  if ADC.read(1) >= 250:
    i = 3           #left

  if ADC.read(1) <= 5:
    i = 4           #right

  if ADC.read(2) == 0:
    i = 5           # Button pressed

  if ADC.read(0) - 125 < 15 and ADC.read(0) - 125 > -15   and ADC.read(1) - 125 < 15 and ADC.read(1) - 125 > -15 and ADC.read(2) == 255:
    i = 0

  return state[i]

if __name__ == '__main__':              # Program start from here
  setup()
  try:
    loop()
  except SystemExit:
    running = False
  except KeyboardInterrupt:       # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
    running = False
    destroy()
