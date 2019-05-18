import tty,termios, fcntl, sys, os

from robot import Robot

class RobotCalibrate:
  def __init__(self, pRobot):
    self.robot = pRobot
    self.robot.Init()

  def Cycle(self):
    x=0
    orig_settings = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin)
    while x != '\x1b':
      x=sys.stdin.read(1)[0]
      print("press key:", x)

      if (x=='`'):
         self.robot.Reset()

      if (x=='3'): self.robot.IncLeg('FL', -10,   0,   0)
      if (x=='e'): self.robot.IncLeg('FL', +10,   0,   0)
      if (x=='2'): self.robot.IncLeg('FL',   0, -10,   0)
      if (x=='w'): self.robot.IncLeg('FL',   0,  10,   0)
      if (x=='1'): self.robot.IncLeg('FL',   0,   0, -10)
      if (x=='q'): self.robot.IncLeg('FL',   0,   0,  10)

      if (x=='6'): self.robot.IncLeg('FR', -10,   0,   0)
      if (x=='y'): self.robot.IncLeg('FR', +10,   0,   0)
      if (x=='7'): self.robot.IncLeg('FR',   0, -10,   0)
      if (x=='u'): self.robot.IncLeg('FR',   0,  10,   0)
      if (x=='8'): self.robot.IncLeg('FR',   0,   0, -10)
      if (x=='i'): self.robot.IncLeg('FR',   0,   0,  10)

      if (x=='d'): self.robot.IncLeg('BL', -10,   0,   0)
      if (x=='c'): self.robot.IncLeg('BL', +10,   0,   0)
      if (x=='s'): self.robot.IncLeg('BL',   0, -10,   0)
      if (x=='x'): self.robot.IncLeg('BL',   0,  10,   0)
      if (x=='a'): self.robot.IncLeg('BL',   0,   0, -10)
      if (x=='z'): self.robot.IncLeg('BL',   0,   0,  10)

      if (x=='h'): self.robot.IncLeg('BR', -10,   0,   0)
      if (x=='n'): self.robot.IncLeg('BR', +10,   0,   0)
      if (x=='j'): self.robot.IncLeg('BR',   0, -10,   0)
      if (x=='m'): self.robot.IncLeg('BR',   0,  10,   0)
      if (x=='k'): self.robot.IncLeg('BR',   0,   0, -10)
      if (x==','): self.robot.IncLeg('BR',   0,   0,  10)


      if (x=='5'): self.robot.IncWBalance(5)
      if (x=='4'): self.robot.IncWBalance(-5)

      if (x=='t'): self.robot.IncWTurn(5)
      if (x=='r'): self.robot.IncWTurn(-5)

      if (x=='g'): self.robot.IncS(10)
      if (x=='b'): self.robot.IncS(-10)


      if (x=='f'): self.robot.IncE(10)
      if (x=='v'): self.robot.IncE(-10)

      if (x==' '): self.robot.printVectors()

      self.robot.apply()

    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, orig_settings)
