import matplotlib.pyplot as plt

# preambule
taille = 20
ratio = 12
fig = plt.figure(figsize=(taille / ratio, taille / ratio / 2))
plt.subplots_adjust(bottom=0, top=1, left=0, right=1, hspace=0.2, wspace=0.2)
plt.axis("off")

# grid
def horizon(a):
    plt.vlines(a, 0, 7)

def vertical(b):
    plt.hlines(b, 0, 5)

plt.vlines(0, 2, 3)
plt.vlines(1, 1, 3)
plt.vlines(2, 0, 3)
plt.vlines(3, 0, 3)
plt.vlines(4, 0, 3)
plt.vlines(5, 0, 2)
plt.vlines(6, 0, 1)
plt.hlines(0, 2, 6)
plt.hlines(1, 1, 6)
plt.hlines(2, 0, 5)
plt.hlines(3, 0, 4)

fig.savefig('m-n-8-little.eps', dpi=100)
