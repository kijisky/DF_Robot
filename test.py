from robot import Robot
from calibrate import RobotCalibrate

r = Robot()
r.Init()

c = RobotCalibrate(r)

print "init ok, start"
c.Cycle()
