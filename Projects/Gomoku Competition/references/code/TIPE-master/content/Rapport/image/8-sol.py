import matplotlib.pyplot as plt

# preambule
taille = 14
ratio = 5
fig = plt.figure(figsize=(taille * 2/ ratio, taille / ratio))
plt.subplots_adjust(bottom=0, top=1, left=0, right=1, hspace=0.2, wspace=0.2)
plt.axis('off')

# Grid
def horizon(a):
    plt.vlines(a, 0, taille, color='grey')

def vertical(b):
    plt.hlines(b, 0, 2 * taille, color='grey')

for i in range(1, taille):
    if i%3 == 1:
        plt.hlines(i, 0, 2 * taille, color='k', linewidth=10 / ratio)
    else:
        vertical(i)
for i in range(1, 2 * taille):
    horizon(i)

# Draw a line between two center
def line(x1, y1, x2, y2):
    if x1 > 2 * taille or y1 > taille or x2 > 2 * taille or y2 > taille or x1 < 0 or y1 < 0 or x2 < 0 or y2 < 0:
        return
    plt.plot([x1, x2], [y1, y2], color='k', linewidth=10 / ratio)

def rightup(x, y):
    line(x, y, x+1, y+1)

def right(x, y):
    if x * y == 0 or x == taille or y == taille:
        return
    line(x, y, x+1, y)

def up(x, y):
    if x * y == 0 or x == taille or y == taille:
        return
    line(x, y, x, y+1)

def rightdown(x, y):
    line(x, y, x+1, y-1)

def zigzag(x, y, dir):
    line(x, y, x, y+1)
    line(x, y+1, x+dir, y+1)
    line(x+dir, y+1, x+dir, y+2)
    line(x+dir, y+2, x+2*dir, y+2)
    line(x+2*dir, y+2, x+2*dir, y+3)

for i in range(-taille, taille):
    for j in range(-taille, taille):
        zigzag(2 + 4 * i, 1 + 6 * j, 1)
        zigzag(2 + 4 * i, 4 + 6 * j, -1)

plt.plot([2.5, 2.5], [1.5, 8.5], color='orange', linewidth=20 / ratio / 2)
plt.plot([5.5, 12.5], [3.5, 10.5], color='orange', linewidth=20 / ratio / 2)
plt.plot([7.5, 14.5], [1.5, 1.5], color='orange', linewidth=20 / ratio / 2)

# Fill with certain color
def fill(x, y, col):
    plt.fill([x, x+1, x+1, x], [y, y, y+1, y+1], color=col)

# Straight fill
fill(2, 3, 'red')
fill(2, 2, 'red')

# Right-up fill
fill(9, 7, 'green')
fill(10, 8, 'green')
fill(11, 9, 'green')

fill(10, 1, 'blue')
fill(11, 1, 'blue')
fill(12, 1, 'blue')
fill(13, 1, 'blue')

# Save image
fig.savefig('8-sol.eps', dpi=100)
plt.show()
