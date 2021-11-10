from matplotlib import pyplot as plt

d = [420, 900, 1000, 1200, 1500, 2060]
d1 = [491.54, 1132.48, 1576.17, 1544.91, 1694.54, 2339.85]
d2 = [701.67, 1333.70, 1750.87, 1541.53, 2046.93, 2456.82]
d3 = [904.6, 1658.89, 1642.55, 1736.52, 2155.82, 2832.99]

D = [d1, d2, d3, d]
E = [[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0]]

for j in range(3):
    for i in range(6):
        E[j][i] = D[j][i] - D[3][i]

plt.plot(D[3], E[0])
plt.plot(D[3], E[1])
plt.plot(D[3], E[2])

plt.legend(["Balise 1", "Balise 2", "Balise 3"], loc='best')
plt.xlabel("Distance réelle")
plt.ylabel("Erreur")
plt.title("Erreur en foction de la distance")
plt.show()
print(D)
print(E)
