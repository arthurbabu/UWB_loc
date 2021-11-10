import serial
import serial.tools.list_ports
import time
import threading

import math
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

import matplotlib.image as mpimg

distribution = []
counter = 0
lastTime = 0
meanFreq = 0
cpt = 0
sumFreq = 0
# Anchor node locations in mm
anchor_x = [0, 0, 10350]
anchor_y = [0,7100,7100]
anchor_z = [0, 0, 0]
anchor = list(zip(anchor_x, anchor_y))

def trilaterate_2D(anchor_x, anchor_y, anchor1, anchor2, anchor3):
    """
    @brief: Trilaterate Tag Location in 2 dimensions
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

    # Solve a linear matrix equation where x,y are the Tag coordinate:
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
    return tag_coordinates


def trilaterate_3D(anchor_x, anchor_y, anchor_z, anchor1, anchor2, anchor3, anchor4):
    """
    @brief: Trilaterate Tag Location in 3 dimensions
    @param: anchor_x - List of anchor coordinates along the X-axis
            anchor_y - List of anchor coordinates along the Y-axis
            anchor_z - List of anchor coordinates along the Z-axis
            anchor1 - Distance to the 1st Anchor
            anchor2 - Distance to the 2nd Anchor
            anchor3 - Distance to the 3rd Anchor
            anchor4 - Distance to the 4rd Anchor
    @ret:   tag_coordinates - Tag Coordinates in a numpy array.
    """
    a1 = np.array([0, 0, 0])
    a2 = np.array([anchor_x[1] - anchor_x[0],
                  anchor_y[1] - anchor_y[0], anchor_z[1] - anchor_z[0]])
    a3 = np.array([anchor_x[2] - anchor_x[0],
                  anchor_y[2] - anchor_y[0], anchor_z[2] - anchor_z[0]])
    v1 = a2 - a1
    v2 = a3 - a1

    Xn = (v1)/np.linalg.norm(v1)

    tmp = np.cross(v1, v2)

    Zn = (tmp)/np.linalg.norm(tmp)

    Yn = np.cross(Xn, Zn)

    i = np.dot(Xn, v2)
    d = np.dot(Xn, v1)
    j = np.dot(Yn, v2)

    X = ((anchor1**2)-(anchor2**2)+(d**2))/(2*d)
    Y = (((anchor1**2)-(anchor3**2)+(i**2)+(j**2))/(2*j))-((i/j)*(X))
    Z1 = np.sqrt(max(0, anchor1**2-X**2-Y**2))
    Z2 = -Z1

    K1 = P1 + X * Xn + Y * Yn + Z1 * Zn
    K2 = P1 + X * Xn + Y * Yn + Z2 * Zn
    return K1,K2
    #return tag_coordinates


# Automatically select J-Link COM port
port = [x for x in serial.tools.list_ports.grep('J-Link', include_links=False)]

# Configure the Serial Port
ser = serial.Serial(
    port=port[0].device,\
    baudrate=115200,\
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
    timeout=None)
print("connected to: " + ser.portstr)


# Set the figure dimensions
fig = plt.figure()
ax = plt.axes(xlim=(-500,11000),ylim=(-500,11000))

# Plot an image containing the room layout
# img = mpimg.imread(
#     '/Users/macbook/Documents/CS/OCENE/SCOC/Projet/DWM1001-Real-Time-Localization-System/img/half10.png')
# imgplot = ax.imshow(img, extent=(-500, 4301-500, -500, 3987-500))

# Plot the anchors and initialize the tag locations.
anchor = np.array(anchor)
# Origin point
scatter = ax.scatter(0, 0, c='blue')
ax.scatter(anchor[:,0], anchor[:,1], c='red')


# Variables used to calculate the average location
previous_value = [(0,0)]
value = 0
samples_to_count = 20
count = 0
total = np.array((0,0))

# Variabales to calculate sliding average
NB_MEAN = 80
index = 0
vals = np.zeros((NB_MEAN, 2))
sum = 0
mean = 0

# Multithreaded serial reading
def in_background():
    while True:
        global value
        value = ser.readline().decode('utf-8', errors='replace')

thread = threading.Thread(target = in_background)
thread.start()

# Filter out corrupted UART data and perform trilateration 
def update(particles, previous_value):
    global value
    global distribution
    global counter
    #print("Raw Data: ",value)
    data = value.split(" | ")
    #print("Data: ", data)
    if(len(data) == 4):
        node1 = data[0].split("=")
        node2 = data[1].split("=")
        node3 = data[2].split("=")
        # print("node1: ", node1)
        # print("node2: ", node2)
        # print("node3: ", node3)
        if (((len(node1) == 2) and (len(node2) == 2) and (len(node3) == 2)) and 
        ((node1[1].isnumeric() == 1) and (node2[1].isnumeric() == 1) and (node3[1].isnumeric() == 1))):
            node1 = int(node1[1])
            node2 = int(node2[1])
            node3 = int(node3[1])
            # print("node1: ", node1)
            # print("node2: ", node2)
            # print("node3: ", node3)
            distribution.append(node1)
            counter += 1
            if counter > 10000 : 
                print(distribution)
                counter = 0
            tag = trilaterate_2D(anchor_x, anchor_y, node1, node2, node3)
            previous_value = tag
            
            global count
            global samples_to_count
            global total

            global sum
            global index
            global vals
            global mean
            global lastTime
            global meanFreq
            global cpt
            global sumFreq
            
            # Sliding average
            sum -= vals[index]
            vals[index] = tag
            sum += vals[index]
            index += 1
            if index > (NB_MEAN - 1):
                index = 0
            mean = sum / NB_MEAN

            '''
            if count < samples_to_count:
                total = total + tag
                count += 1
            if count == samples_to_count:
                total /= samples_to_count
                scatter.set_offsets(total)
                total = np.array((0,0))
                count = 0
            '''

            scatter.set_offsets(mean)
            print("Tag coordinates : ", mean)
            currentTime = time.perf_counter()
            sumFreq += 1/(currentTime - lastTime)
            cpt += 1
            meanFreq = sumFreq/cpt
            print("Freq = "+str(meanFreq))
            lastTime = currentTime
        else:
            print("Node Length / Int Error")
            tag = previous_value
    else:
        print("Error : only 3 nodes")
        tag = previous_value

    return scatter,

anim = FuncAnimation(fig, update, interval = 1, fargs= previous_value, blit = True)

plt.show()
