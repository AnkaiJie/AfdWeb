import numpy as np
import matplotlib.pyplot as plt

# some labels for each row
people = ('A','B','C','D','E','F','G','H')
r = len(people)

# how many data points overall (average of 3 per person)
n = r * 3

# which person does each segment belong to?
rows = np.random.randint(0, r, (n,))
# how wide is the segment?
widths = np.random.randint(3,12, n,)
# what label to put on the segment
labels = range(n)
colors ='rgbwmc'

patch_handles = []

fig = plt.figure(figsize=(10,8))
ax = fig.add_subplot(111)



left = np.zeros(r,)
row_counts = np.zeros(r,)

for (r, w, l) in zip(rows, widths, labels):
    print (r, w, l)
    patch_handles.append(ax.barh(r, w, align='center', left=left[r],
        color=colors[int(row_counts[r]) % len(colors)]))
    left[r] += w
    row_counts[r] += 1
    # we know there is only one patch but could enumerate if expanded
    patch = patch_handles[-1][0] 
    bl = patch.get_xy()
    x = 0.5*patch.get_width() + bl[0]
    y = 0.5*patch.get_height() + bl[1]
    ax.text(x, y, "%d%%" % (l), ha='center',va='center')

y_pos = np.arange(8)
ax.set_yticks(y_pos)
ax.set_yticklabels(people)
ax.set_xlabel('Distance')

plt.show()
