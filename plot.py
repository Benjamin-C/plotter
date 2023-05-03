from machine import Plotter
import time
import random

p = Plotter('/dev/ttyUSB1', True)

# print("Moving")
# p.g0(random.randint(30, 100), random.randint(30, 100))

# p.waitForCompletion()
# time.sleep(0.25)
# p.cmd()

# p.home()

# print("Plotting")

# p.home()
# p.cmd("g0 x100 y100")
# p.waitForCompletion()

# p.plotText("A", width=15, spacing=3)
# p.waitForCompletion()

p.readPos()
print("DONE WAITING NOW CAN I END?")

# p.plotPreview()
# p.savegcode()

input()
p.close()
