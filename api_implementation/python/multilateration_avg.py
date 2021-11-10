# https://github.com/jurasofish/multilateration/blob/master/multilateration.ipynb

from multilaterate import get_loci
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import least_squares

# Number of towers
num_towers = 4

# Metre length of a square containing the transmitting
# device, centred around (x, y) = (0, 0).
tx_square_side = 20

# Metre length of a square containing the towers,
# centred around (x, y) = (0, 0).
rx_square_side = 20

# Speed of light for radio signals.
v= 299792458

# Metre increments to radii of circles when generating locus of
# circle intersection.
delta_d = int(100)

# Max distance a transmission will be from the tower that first
# received the transmission. This puts an upper bound on the radii of the
# circle, thus limiting the size of the locus to be near the towers.
max_d = int(20)

# Whether to plot circles that would be
# used if performing trilateration. These are circles that are centred
# on the towers and touch the transmitter site.
plot_trilateration_circles = False

# Whether to plot a straight line
# between every pair of towers. This is useful for visualising the
# hyperbolic loci focal points.
plot_lines_between_towers = False


########### Plotting ###########
# Anchor location in mm 
# with tower i: x = towers[i][0], y = towers[i][1]
towers = np.array([[0, 0], [0, 7100], [10350, 7100], [7100, 0]])
print('towers:\n', towers)

# Tag location in mm with tag i : x = tx[0], y = tx[1]
tx = np.array([5000, 5000])
print('tx:', tx)

# Retrieve distance from tag through serial port
# distances[i] is distance from tower i to transmitter.
# TODO create un numpy array
distances = np.array([])

# Time at which each tower receives the transmission.
rec_times = distances/v
print('rec_times:', rec_times)

# Get the loci.
loci = get_loci(rec_times, towers, v, delta_d, max_d)

# Plot towers and transmission location.
fig, ax = plt.subplots(figsize=(5, 5))
max_width = max(tx_square_side, rx_square_side)/2
ax.set_ylim((max_width*-1, max_width))
ax.set_xlim((max_width*-1, max_width))
for i in range(towers.shape[0]):
    x = towers[i][0]
    y = towers[i][1]
    ax.scatter(x, y)
    ax.annotate('Tower '+str(i), (x, y))
ax.scatter(tx[0], tx[1])
ax.annotate('Tx', (tx[0], tx[1]))

# Iterate over every unique combination of towers and plot nifty stuff.
for i in range(num_towers):
    if(plot_trilateration_circles):
        # Circle from tower i to tx site
        circle1 = (towers[i][0], towers[i][1], distances[i])
        circle = plt.Circle((circle1[0], circle1[1]),
                            radius=circle1[2], fill=False)
        ax.add_artist(circle)
    for j in range(i+1, num_towers):
        if(plot_lines_between_towers):
            # Line between towers
            ax.plot((towers[i][0], towers[j][0]),
                    (towers[i][1], towers[j][1]))

for locus in loci:
    ax.plot(locus[0], locus[1])
plt.show()



# Solve the location of the transmitter.

c = np.argmin(rec_times)
p_c = np.expand_dims(towers[c], axis=0)
t_c = rec_times[c]

# Remove the c tower to allow for vectorization.
all_p_i = np.delete(towers, c, axis=0)
all_t_i = np.delete(rec_times, c, axis=0)


def eval_solution(x):
    """ x is 2 element array of x, y of the transmitter"""
    return (
        np.linalg.norm(x - p_c, axis=1)
        - np.linalg.norm(x - all_p_i, axis=1)
        + v*(all_t_i - t_c)
    )


# Initial guess.
x_init = [0, 0]

# Find a value of x such that eval_solution is minimized.
# Remember the receive times have error added to them: rec_time_noise_stdd.
res = least_squares(eval_solution, x_init)

print(f"Actual emitter location:    ({tx[0]:.1f}, {tx[1]:.1f}) ")
print(f"Calculated emitter locaion: ({res.x[0]:.1f}, {res.x[1]:.1f})")
print(f"Error in metres:            {np.linalg.norm(tx-res.x):.1f}")

# And now plot the solution.
fig, ax = plt.subplots(figsize=(5, 5))
max_width = max(tx_square_side, rx_square_side)/2
ax.set_ylim((max_width*-1, max_width))
ax.set_xlim((max_width*-1, max_width))

for locus in loci:
    ax.plot(locus[0], locus[1])

ax.scatter(tx[0], tx[1], color='red')
ax.annotate('Actual', (tx[0], tx[1]))

ax.scatter(res.x[0], res.x[1], color='blue')
ax.annotate('Solved', (res.x[0], res.x[1]))

plt.show()
