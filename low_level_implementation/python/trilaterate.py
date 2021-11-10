import serial
import numpy as np
import matplotlib.pyplot as plt
from threading import Thread
import matplotlib.animation as animation

### PARAMETERS ###

anchor_x = [0,10000,10000]       # Anchors X position
anchor_y = [0,0,6600]       # Anchors Y position

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

X = []
Y = []
DIST = [0,0,0]

class datas_collect(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        global X
        global Y
        global DIST
        ser = serial.Serial(
            port='/dev/cu.usbmodem0007600442391',\
            baudrate=115200,\
            parity=serial.PARITY_NONE,\
            stopbits=serial.STOPBITS_ONE,\
            bytesize=serial.EIGHTBITS,\
                timeout=0)

        print("connected to: " + ser.portstr)

        line = []

        distances = {}
        distances['D1'] = -1
        distances['D2'] = -1
        distances['D3'] = -1

        tag = [0,0]
        tags = [[0,0],[0,0],[0,0]]

        temp_X = 0
        temp_Y = 0
        temp_dist = [0, 0, 0]
        temp_cpt = 0

        while 1:
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
                        print(tag)
                        print(distances)
                        if temp_cpt < 3:
                            temp_X += tag[0]
                            temp_Y += tag[1]
                            temp_dist[0] += distances['D1']
                            temp_dist[1] += distances['D2']
                            temp_dist[2] += distances['D3']
                            temp_cpt += 1
                        else:
                            temp_cpt = 0
                            X.append(temp_X/3)
                            Y.append(temp_Y/3)
                            temp_X = 0
                            temp_Y = 0
                            DIST[0] = temp_dist[0]/3
                            DIST[1] = temp_dist[1]/3
                            DIST[2] = temp_dist[2]/3
                            temp_dist[0] = 0
                            temp_dist[1] = 0
                            temp_dist[2] = 0


                    line = []

'''
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

tag = [0,0]
tags = [[0,0],[0,0],[0,0]]
X = []
Y = []
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
                print(tag)
                print(distances)
                X.append(tag[0])
                Y.append(tag[1])
                cpt+=1
            line = []

ser.close()
plt.scatter(X,Y)
plt.show()

X = np.array(X)
Y = np.array(Y)

'''

# Création des threads
thread_1 = datas_collect()

# Lancement des threads
thread_1.start()

fig = plt.figure() # initialise la figure
plt.scatter(anchor_x,anchor_y, color='red')
circles_line_1 = plt.Circle((anchor_x[0],anchor_y[0]),1000)
circles_line_2 = plt.Circle((anchor_x[1],anchor_y[1]),0)
circles_line_3 = plt.Circle((anchor_x[2],anchor_y[2]),0)
line, = plt.plot([], [])

plt.xlim(-2000, 11000)
plt.ylim(-2000, 8000)

def animate(i):
    line.set_data(X, Y)
    circles_line_1.set_radius(DIST[0])
    circles_line_2.set_radius(DIST[1])
    circles_line_3.set_radius(DIST[2])
    return line,

ani = animation.FuncAnimation(fig, animate, frames=1000, blit=True, interval=500, repeat=False)

plt.show()



