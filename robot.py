from __future__ import division

import time
import Adafruit_PCA9685

class Robot:
  def __init__(self):
    self.stateVersion = 1
    self.pwm = Adafruit_PCA9685.PCA9685()
    self.pwm.set_pwm_freq(60)


    # states Array
    self.statesList = []
    # init state Vector
    self.iV = [540-0, 320+0, 140+0, 0, # LF
               250+0, 560-0, 610-0, 0,   # RF
               560-0, 460+0, 200+0, 0,   # LB
               260+0, 450-0, 640-0, 0 ]  # RB
    # diff state Vector
    self.dV = [0,0,0,0,  0,0,0,0, 0,0,0,0, 0,0,0,0]
    # shoulders forward offset
    self.sf=-50
    # shoulders backside offset
    self.sb=0
    # wings balance
    self.wb=10
    # winds turn
    self.wt=0
    # all shoulders offset (forward, backward)
    self.s=-20
    # all elbows offset
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

  def pushState(self):
    curState = self.getState()
    self.statesList.append(curState)

  def playStates(self):
    print("play states")
    self.Reset()
    time.sleep(1)
    self.apply()
    for state in self.statesList:
      print("next state")
      self.loadState(state)
      time.sleep(0.4)

  def dumpStates(self):
    for state in self.statesList:
      print("state:", state)


