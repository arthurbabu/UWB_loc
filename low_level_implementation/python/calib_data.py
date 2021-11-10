import serial
import numpy as np
import logging as log

### PARAMETERS ###

real_dist = 1200        # Real distance between tag and anchors
NB_SAMPLES = 100        # Samples number for statistics


log.basicConfig(filename='log.log', encoding='utf-8', level=log.INFO, format="%(levelname)s %(message)s")

def readDistance(ser):
    line = []
    end = False
    while not(end):
        for c in ser.read():
            c = chr(c)
            line.append(c)
            if c == '\n':
                line.pop(-1)
                line_str = ''.join(line)
                end = True

    return int(line_str)

ser = serial.Serial(
    port='/dev/cu.usbmodem0007600442391',\
    baudrate=115200,\
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
        timeout=0)

print("connected to: " + ser.portstr)
count=1
line = []

distances = {}
distances['D1'] = -1
distances['D2'] = -1
distances['D3'] = -1

tags = [[0,0],[0,0],[0,0]]
D = [[],[],[]]
cpt = 0

while cpt < NB_SAMPLES:
    for c in ser.read():
        c = chr(c)
        line.append(c)
        if c == '\n':
            line.pop(-1)
            line_str = ''.join(line)
            if line_str=='D1':
                distances['D1'] = readDistance(ser)
            if line_str=='D2':
                distances['D2'] = readDistance(ser)
            if line_str=='D3':
                distances['D3'] = readDistance(ser)
                D[0].append(distances['D1'])
                D[1].append(distances['D2'])
                D[2].append(distances['D3'])
                print(distances)
                cpt+=1
            line = []

ser.close()

D[0].pop(0)
D[1].pop(0)
D[1].pop(0)

log.info("###############################################################")
log.info('Distance réelle : '+str(real_dist))
log.info('axe D1 :')
log.info('mean :'+str(np.mean(D[0])))
log.info('std :'+str(np.std(D[0])))
log.info('min :'+str(np.min(D[0])))
log.info('max :'+str(np.max(D[0])))
log.info('axe D2 :')
log.info('mean :'+str(np.mean(D[1])))
log.info('std :'+str(np.std(D[1])))
log.info('min :'+str(np.min(D[1])))
log.info('max :'+str(np.max(D[1])))
log.info('axe D3 :')
log.info('mean :'+str(np.mean(D[2])))
log.info('std :'+str(np.std(D[2])))
log.info('min :'+str(np.min(D[2])))
log.info('max :'+str(np.max(D[2])))




