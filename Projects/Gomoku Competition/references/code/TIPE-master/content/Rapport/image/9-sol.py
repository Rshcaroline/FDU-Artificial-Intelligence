import matplotlib.pyplot as plt

# preambule
taille = 15
ratio = 5
fig = plt.figure(figsize=(taille / ratio, taille / ratio))
plt.subplots_adjust(bottom=0, top=1, left=0, right=1, hspace=0.2, wspace=0.2)
plt.axis('off')

# Grid
def horizon(a):
    plt.vlines(a, 0, taille)

def vertical(b):
    plt.hlines(b, 0, taille)

for i in range(taille):
    horizon(i + 0.5)
    vertical(i + 0.5)

# Draw a line between two center
def line(x1, y1, x2, y2):
    if x1 > taille or y1 > taille or x2 > taille or y2 > taille or x1 < 0 or y1 < 0 or x2 < 0 or y2 < 0:
        return
    plt.plot([x1, x2], [y1, y2], color='grey', linewidth=20 / ratio)

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

for i in range(-taille, taille):
    for j in range(-taille, taille):
        rightup(2*i, 4*j + i)
        rightdown(2*i, 4*j + 3 - i)
    # Right
        right(1 + 8*i, 8*j - 4*i)
        right(1 + 8*i, 8*j - 4*i - 1)
        right(3 + 8*i, 8*j - 4*i - 4)
        right(3 + 8*i, 8*j - 4*i - 5)
        right(5 + 8*i, 8*j - 4*i - 2)
        right(5 + 8*i, 8*j - 4*i - 3)
        right(7 + 8*i, 8*j - 4*i + 2)
        right(7 + 8*i, 8*j - 4*i + 1)
    # Up
        up(1 + 8*i, 8*j - 4*i + 3)
        up(2 + 8*i, 8*j - 4*i + 3)
        up(3 + 8*i, 8*j - 4*i - 1)
        up(4 + 8*i, 8*j - 4*i - 1)
        up(5 + 8*i, 8*j - 4*i + 1)
        up(6 + 8*i, 8*j - 4*i + 1)
        up(7 + 8*i, 8*j - 4*i - 3)
        up(8 + 8*i, 8*j - 4*i - 3)

plt.plot([2, 2], [1, 9], color='red', linewidth=20 / ratio / 2)
plt.plot([5, 13], [3, 11], color='red', linewidth=20 / ratio / 2)

# Save image
fig.savefig('m-n-9.eps', dpi=100)
