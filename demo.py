#!/usr/bin/env python

import RPi.GPIO as GPIO
import LCD1602
import PCF8591 as ADC
import time
import math

TRIG = 11
ECHO = 12

def setup():
  LCD1602.init(0x27, 1)   # init(slave address, background light)
  LCD1602.write(0, 0, 'Greeting!!')
  LCD1602.write(1, 1, 'Drone :-)')

  ADC.setup(0x48)                                 # Setup PCF8591

  GPIO.setmode(GPIO.BOARD)
  GPIO.setup(TRIG, GPIO.OUT)
  GPIO.setup(ECHO, GPIO.IN)

  global state
  global current_dist
  global running

def showDirect(direction):
  LCD1602.clear()
  LCD1602.write(0, 0, 'AR Drone Going!!')
  LCD1602.write(1, 1, direction)

def loop():
  running = True
  status = '';
  current_dist = distance()
  while running:
    try:
      d = direction()
      dis = distance()
      if d == 'pressed':
        print 'pressed', dis
        running = False

      if dis >= 0 and dis <= 100 and current_dist >= 0 and current_dist <= 100:
        if dis >= 0 and dis <= 50:
          if dis > current_dist:
            print 'drone up', dis, current_dist
            showDirect('up %d' % dis) 
          elif dis < current_dist:
            print 'drone down', dis, current_dist
            showDirect('down %d' % dis) 

      if status != '' and status != d:
        showDirect(d)
      status = d
      current_dist = dis
      time.sleep(0.1)
    except:
      pass

  print "Shutting down...",
  print "Ok."
  showDirect('landed')
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
    GPIO.cleanup()
  except KeyboardInterrupt:       # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
    running = False
    GPIO.cleanup()
