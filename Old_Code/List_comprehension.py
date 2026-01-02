# a = 0
# zahl_liste = [1, 2, 3, 4, 5, 6, 7, 8]
# liste1 = [x * 2 for x in zahl_liste ]
# print(liste1)
# students = ["Max", "Monika", "Erik", "Tim", "Brain"]
# lengts = [len(x) for x in students]
# print(lengts)
import matplotlib.pyplot as  plt
xs = [x for x in range (-99, 100)]
ys = [x **2 for x in range (-99, 100)]
ys1 = [(x **2) / 2 for x in range (-99, 100)]
xs0 = [x * 0 for x in range(-99, 100)]
print(ys1)
plt.plot(xs, ys)
plt.plot(xs, ys1)
plt.plot(xs0, ys)
plt.show()

