from time import sleep
import sys

# https://stackoverflow.com/questions/3002085/python-to-print-out-status-bar-and-percentage
def drawProgressBar(percent, barLen = 20):
    # percent float from 0 to 1. 
    sys.stdout.write("\r")
    progress = ""
    sys.stdout.write("[{:<{}}] {:.0f}%".format("=" * int(barLen * percent), barLen, percent * 100))
    sys.stdout.flush()

for i in range(101):
    drawProgressBar( i/100)
    sleep(0.01)
