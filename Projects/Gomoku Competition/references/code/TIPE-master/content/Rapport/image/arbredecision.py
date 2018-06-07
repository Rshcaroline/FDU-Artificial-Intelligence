import matplotlib.pyplot as plt

# preambule
taille = 68
ratio = 20
fig = plt.figure(figsize=(taille / ratio, taille / ratio))
plt.subplots_adjust(bottom=0, top=1, left=0, right=1, hspace=0.2, wspace=0.2)
plt.axis('off')
ax = plt.gca()
ax.cla()
ax.spines['top'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)


# Draw a line between two center
def line(x1, y1, x2, y2, col):
    plt.plot([x1, x2], [y1, y2], color=col, linewidth=20 / ratio)

def jeu(x, y):
    for i in range(4):
        line(x + i, y, x + i, y + 3, 'black')
        line(x, y + i, x + 3, y + i, 'black')
jeu(0, 0)
jeu(4, 0)
jeu(2, 4)
jeu(7, 4)
jeu(12, 4)
jeu(7, 8)
line(1.5, 3, 3, 4, 'black')
line(5.5, 3, 4, 4, 'black')
line(3.5, 7, 7.5, 8, 'black')
line(8.5, 7, 8.5, 8, 'black')
line(13.5, 7, 9.5, 8, 'black')
line(1, 0, 0.5, -1, 'black')
line(2, 0, 2.5, -1, 'black')
line(5, 0, 4.5, -1, 'black')
line(6, 0, 6.5, -1, 'black')
line(8, 4, 7.5, 3, 'black')
line(9, 4, 9.5, 3, 'black')
line(13, 4, 12.5, 3, 'black')
line(14, 4, 14.5, 3, 'black')

# Circle
def black(x, y):
    ax.add_artist(plt.Circle((x + 0.5, y + 0.5), (0.35), color='black'))

def white(x, y):
    ax.add_artist(plt.Circle((x + 0.5, y + 0.5), (0.35), color='black', fill=False))

black(1, 1)
white(0, 2)
black(5, 1)
white(5, 2)
black(3, 5)
black(7, 5)
black(12, 6)

#plt.plot([2, 2], [1, 9], color='black', linewidth=20 / ratio / 2)
#plt.plot([5, 13], [3, 11], color='black', linewidth=20 / ratio / 2)

# Save image
fig.savefig('arbre.eps', dpi=100)
