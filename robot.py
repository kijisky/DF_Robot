from __future__ import division

import time
import tty,termios, fcntl, sys, os
import Adafruit_PCA9685

class Robot:
  def __init__(self):
    self.stateVersion = 1
    self.pwm = Adafruit_PCA9685.PCA9685()
    self.servo_min = 80 #80  # Min pulse length out of 4096
    self.servo_max = 80 #400  # Max pulse length out of 4096

    self.pwm.set_pwm_freq(60)

    self.iV = [540-0, 400+0, 140+0, 0,   # LF
      250+0, 480-0, 610-0, 0,   # RF
      590-0, 460+0, 200+0, 0,   # LB
      220+0, 450-0, 640-0, 0 ]  # RB
    self.dV = [0,0,0,0,  0,0,0,0, 0,0,0,0, 0,0,0,0]

    self.sf=-50
    self.sb=0
    self.wb=10
    self.wt=0
    self.s=-20
    self.e=0

  def Reset(self):
    self.SetLeg('FL', 0,0,0)
    self.SetLeg('FR', 0,0,0)
    self.SetLeg('BL', 0,0,0)
    self.SetLeg('BR', 0,0,0)
    self.SetWBalance(0)
    self.SetWTurn(0)
    self.SetShoulder(0)
    self.SetElbow(0)
    self.apply()

  def set_servo_pulse(self,channel, pulse):
    pulse_length = 1000000    # 1,000,000 us per second
    pulse_length //= 60       # 60 Hz
    print('{0}us per period'.format(pulse_length))
    pulse_length //= 4096     # 12 bits of resolution
    print('{0}us per bit'.format(pulse_length))
    pulse *= 1000
    pulse //= pulse_length
    self.pwm.set_pwm(channel, 0, pulse)


  def setVector(self, vec):
    for i in range(0,16):
      self.pwm.set_pwm(i, 0, vec[i])

  def getRawVector(self):
    diffV = [ -self.dV[0],  self.dV[1],  self.dV[2], 0,
               self.dV[4], -self.dV[5], -self.dV[6], 0,
              -self.dV[8],  self.dV[9],  self.dV[10],0,
               self.dV[12],-self.dV[13],-self.dV[14],0]
    offsetV = [ 0-self.wb-self.wt, 0+self.s+self.sf, 0+self.e, 0,
                0-self.wb-self.wt, 0-self.s-self.sf, 0-self.e, 0,
                0-self.wb+self.wt, 0+self.s+self.sb, 0+self.e, 0,
                0-self.wb+self.wt, 0-self.s-self.sb, 0-self.e, 0 ]

    ans =  [x+y+z for x,y,z in zip(self.iV, diffV, offsetV)]
    return ans

  def printVectors(self):
    print("wb: ",  self.wb, "wt: ",  self.wt, "s: ", self.s, "e: ", self.e)
    print("FL:", self.dV[0:3],   " FR: ", self.dV[4:7])
    print("BL:", self.dV[8:11],  " BR: ", self.dV[12:15])
    print("raw:", self.getRawVector())

  def getState(self):
    version = [self.stateVersion]
    xV = [self.wb, self.wt, self.s, self.e]
    ans = version + xV + self.dV
    return ans;

  def loadState(self, pStateArr):
    version = pStateArr[0]
    if (version == self.stateVersion):
      self.wb = pStateArr[1]
      self.wt = pStateArr[2]
      self.s = pStateArr[3]
      self.e = pStateArr[4]
      self.dV = pStateArr[5:21]
      self.apply()


  def apply(self):
    rawVect = self.getRawVector()
    self.setVector(rawVect)

  def Init(self):
    self.Reset()
    self.apply()
    time.sleep(1)

  def GetLegIndex(self, pLeg):
    if (pLeg == 'FL' or pLeg == 'LF'):
      return 0
    if (pLeg == 'FR' or pLeg == 'RF'):
      return 4
    if (pLeg == 'BL' or pLeg == 'LB'):
      return 8
    if (pLeg == 'BR' or pLeg == 'RB'):
      return 12
    return 0

  def SetLeg(self, pLeg, w,s,e):
    indx= self.GetLegIndex(pLeg)
    self.dV[indx+0]=w
    self.dV[indx+1]=s
    self.dV[indx+2]=e

  def IncLeg(self, pLeg, w,s,e):
    print("inc", pLeg, w,s,e)
    indx= self.GetLegIndex(pLeg)
    self.dV[indx+0]= self.dV[indx+0] + w
    self.dV[indx+1]= self.dV[indx+1] + s
    self.dV[indx+2]= self.dV[indx+2] + e

  def SetWBalance(self, pVal):
    self.wb = pVal

  def IncWBalance(self, pVal):
    self.wb += pVal

  def SetWTurn(self, pVal):
    self.wt = pVal

  def IncWTurn(self, pVal):
    self.wt += pVal


  def SetShoulder(self, pVal):
    self.s = pVal

  def IncShoulder(self, pVal):
    self.s += pVal

  def SetElbow(self, pVal):
    self.e = pVal

  def IncElbow(self, pVal):
    self.e += pVal
