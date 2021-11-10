import serial
import time
import threading

import math
from sklearn.metrics import euclidean_distances
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

import matplotlib.image as mpimg

import logging as log

log.basicConfig(filename='log.log', encoding='utf-8', level=log.INFO, format="%(levelname)s %(message)s")

def trilaterate(anchor_x, anchor_y, anchor1, anchor2, anchor3):
    """
    @brief: Trilaterate Tag location
    @param: anchor_x - List of anchor coordinates along the X-axis
            anchor_y - List of anchor coordinates along the Y-axis
            anchor1 - Distance to the 1st Anchor
            anchor2 - Distance to the 2nd Anchor
            anchor3 - Distance to the 3rd Anchor
    @ret:   tag_coordinates - Tag Coordinates in a numpy array.
    """
    r1_sq = pow(anchor1,2)
    r2_sq = pow(anchor2,2)
    r3_sq = pow(anchor3,2)

    # Solve a linear matrix equation where x,y is the Tag coordinate:
    # Ax + By = C
    # Dx + Ey = F
    A = (-2*anchor_x[0]) + (2*anchor_x[1])
    B = (-2*anchor_y[0]) + (2*anchor_y[1])
    C = r1_sq - r2_sq - pow(anchor_x[0],2) + pow(anchor_x[1],2) - pow(anchor_y[0],2) + pow(anchor_y[1],2)
    D = (-2*anchor_x[1]) + (2*anchor_x[2])
    E = (-2*anchor_y[1]) + (2*anchor_y[2])
    F = r2_sq - r3_sq - pow(anchor_x[1],2) + pow(anchor_x[2],2) - pow(anchor_y[1],2) + pow(anchor_y[2],2)

    a = np.array([[A, B], [D, E]])
    b = np.array([C, F])
    tag_coordinates = np.linalg.solve(a, b)
    # print("Tag Coordinate:", tag_coordinates)
    return tag_coordinates

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
    port='/dev/cu.usbmodem0007600390051',\
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

anchor_x = [0,6000,0]
anchor_y = [0,0,4000]
tag = [0,0]
tags = [[0,0],[0,0],[0,0]]
X = []
Y = []
D = [[],[],[]]
cpt = 0

while cpt < 100:
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
                tag = trilaterate(anchor_x, anchor_y, distances['D1'], distances['D2'], distances['D3'])
                D[0].append(distances['D1'])
                D[1].append(distances['D2'])
                D[2].append(distances['D3'])
                print(tag)
                print(distances)
                #tags.pop(0)
                #tags.append(tag)
                #x = 0
                #y = 0
                #for e in tags:
                #    x+=e[0]
                #    y+=e[1]

                #X.append(x/len(tags))
                #Y.append(y/len(tags))
                X.append(tag[0])
                Y.append(tag[1])
                cpt+=1
            line = []

ser.close()
plt.scatter(X,Y)
plt.show()

X = np.array(X)
Y = np.array(Y)

D[0].pop(0)
D[1].pop(0)
D[1].pop(0)
real_dist = 1200

log.info("###############################################################")
log.info('Distance réelle : '+str(real_dist))
log.info('axe X :')
log.info('mean :'+str(np.mean(X)))
log.info('std :'+str(np.std(X)))
log.info('min :'+str(np.min(X)))
log.info('max :'+str(np.max(X)))
log.info('axe Y :')
log.info('mean :'+str(np.mean(Y)))
log.info('std :'+str(np.std(Y)))
log.info('min :'+str(np.min(Y)))
log.info('max :'+str(np.max(Y)))
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




