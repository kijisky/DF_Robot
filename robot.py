from __future__ import division

import time
import tty,termios, fcntl, sys, os
import Adafruit_PCA9685

class Robot:
  def __init__(self):
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
    self.w=10
    self.s=-20
    self.e=0


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

  def calcVector(self, flw, fls, fle, frw, frs, fre, blw, bls, ble, brw, brs, bre):
    ans = [  self.iV[0]  - flw - self.w, self.iV[1]  + fls +self.s +self.sf, self.iV[2]  + fle + self.e, 0,  # LF
             self.iV[4]  + frw - self.w, self.iV[5]  - frs -self.s -self.sf, self.iV[6]  - fre - self.e, 0,  # RF
             self.iV[8]  - blw - self.w, self.iV[9]  + bls +self.s +self.sb, self.iV[10] + ble + self.e, 0,  # LB
             self.iV[12] + brw - self.w, self.iV[13] - brs -self.s -self.sb, self.iV[14] - bre - self.e, 0   # RB
    ]
    return ans;

  def printVectors(self):
    diffV = [ -self.dV[0],  self.dV[1],  self.dV[2], 0,
               self.dV[4], -self.dV[5], -self.dV[6], 0,
              -self.dV[8],  self.dV[9],  self.dV[10],0,
               self.dV[12],-self.dV[13],-self.dV[14],0]
    offsetV = [ 0-self.w, 0+self.s+self.sf, 0+self.e, 0,
                0-self.w, 0-self.s-self.sf, 0-self.e, 0,
                0-self.w, 0+self.s+self.sb, 0+self.e, 0,
                0-self.w, 0-self.s-self.sb, 0-self.e, 0 ]
    ans =  [y+z for y,z in zip(dV, offsetV)]

    print("dV:")
    print(ans[0],  ans[1],  ans[2]);
    print(ans[4],  ans[5],  ans[6]);
    print(ans[8],  ans[9],  ans[10]);
    print(ans[12], ans[13], ans[14]);


  def applyVector(self):
    diffV = [ -self.dV[0],  self.dV[1],  self.dV[2], 0,
               self.dV[4], -self.dV[5], -self.dV[6], 0,
              -self.dV[8],  self.dV[9],  self.dV[10],0,
               self.dV[12],-self.dV[13],-self.dV[14],0]
    offsetV = [ 0-self.w, 0+self.s+self.sf, 0+self.e, 0,
                0-self.w, 0-self.s-self.sf, 0-self.e, 0,
                0-self.w, 0+self.s+self.sb, 0+self.e, 0,
                0-self.w, 0-self.s-self.sb, 0-self.e, 0 ]

    ans =  [x+y+z for x,y,z in zip(self.iV, diffV, offsetV)]
    self.setVector(ans)

  def doVector(self, flw, fls, fle, frw, frs, fre, blw, bls, ble, brw, brs, bre):
    v = self.calcVector( flw, fls, fle, frw, frs, fre, blw, bls, ble, brw, brs, bre)
    self.setVector(v);


  def doSit(self):
    self.doVector(0,0,0, 0,0,0,  0,0,0, 0,0,0);
    time.sleep(1)
    self.doVector(-30,100,150, -30,100,150,  30,-50,150, 30,-50,150);
    time.sleep(1)


  def Init(self):
    self.doVector(0,0,0,  0,0,0,  0,0,0, 0,0,0);
    time.sleep(1)

  def GetLegIndex(self, pLeg):
    if (pLeg == 'FL'):
      return 0
    if (pLeg == 'FR'):
      return 4
    if (pLeg == 'BL'):
      return 8
    if (pLeg == 'BR'):
      return 12
    return 0

  def SetLeg(self, pLeg, w,s,e):
    indx= self.GetLegIndex(pLeg)
    self.dV[indx+0]=w
    self.dV[indx+1]=s
    self.dV[indx+2]=e

  def IncLeg(self, pLeg, w,s,e):
    print("inc", pLeg, w,s,e)
    indx= GetLegIndex(pLeg)
    self.dV[indx+0]= self.dV[indx+0] + w
    self.dV[indx+1]= self.dV[indx+1] + s
    self.dV[indx+2]= self.dV[indx+2] + e

  def Calibrate(self):
    global w,s,e
    x=0
    selChan=''
    orig_settings = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin)
    while x != '\x1b':
      x=sys.stdin.read(1)[0]
      if (x=='1'): selChan='FL'
      if (x=='2'): selChan='FR'
      if (x=='3'): selChan='BL'
      if (x=='4'): selChan='BR'
      if (x=='`'):
         SetLeg('FL', 0,0,0)
         SetLeg('FR', 0,0,0)
         SetLeg('BL', 0,0,0)
         SetLeg('BR', 0,0,0)
         w=0
         s=0
         e=0

      if (x=='3'): IncLeg('FL', -10,   0,   0)
      if (x=='e'): IncLeg('FL', +10,   0,   0)
      if (x=='2'): IncLeg('FL',   0, -10,   0)
      if (x=='w'): IncLeg('FL',   0,  10,   0)
      if (x=='1'): IncLeg('FL',   0,   0, -10)
      if (x=='q'): IncLeg('FL',   0,   0,  10)

      if (x=='6'): IncLeg('FR', -10,   0,   0)
      if (x=='y'): IncLeg('FR', +10,   0,   0)
      if (x=='7'): IncLeg('FR',   0, -10,   0)
      if (x=='u'): IncLeg('FR',   0,  10,   0)
      if (x=='8'): IncLeg('FR',   0,   0, -10)
      if (x=='i'): IncLeg('FR',   0,   0,  10)

      if (x=='d'): IncLeg('BL', -10,   0,   0)
      if (x=='c'): IncLeg('BL', +10,   0,   0)
      if (x=='s'): IncLeg('BL',   0, -10,   0)
      if (x=='x'): IncLeg('BL',   0,  10,   0)
      if (x=='a'): IncLeg('BL',   0,   0, -10)
      if (x=='z'): IncLeg('BL',   0,   0,  10)

      if (x=='h'): self.IncLeg('BR', -10,   0,   0)
      if (x=='n'): self.IncLeg('BR', +10,   0,   0)
      if (x=='j'): self.IncLeg('BR',   0, -10,   0)
      if (x=='m'): self.IncLeg('BR',   0,  10,   0)
      if (x=='k'): self.IncLeg('BR',   0,   0, -10)
      if (x==','): self.IncLeg('BR',   0,   0,  10)


      if (x=='5'): w-=5
      if (x=='4'): w+=5

      if (x=='t'): s+=10
      if (x=='g'): s-=10


      if (x=='l'): e+=10
      if (x=='.'): e-=10

      if (x==' '): printVectors()
      self.applyVector()

      print("key", x)
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, orig_settings)
