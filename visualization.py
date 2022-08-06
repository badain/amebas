# Imports
# utilities
import numpy as np
# visualization
from matplotlib import pyplot as plt

# Visualization Functions
# Display Image Helper Function
def display(image, title, ts, id, workDir, colorMap):
    fig, axes = plt.subplots(nrows=1, ncols=3, sharex=True, sharey=True)
    plt.suptitle(title, fontsize=18)
    ax = axes.ravel()
    if(colorMap == "turbo"): cmap = plt.cm.turbo
    else: cmap = plt.cm.gray

    ax[0].imshow(image[0,:,:], cmap=cmap)
    ax[0].axis('off')
    ax[0].set_title("0", fontsize=14)

    half = int(np.floor(image.shape[0] / 2))
    ax[1].imshow(image[half,:,:], cmap=cmap)
    ax[1].axis('off')
    ax[1].set_title(f"{half}", fontsize=14)

    ax[2].imshow(image[image.shape[0]-1,:,:], cmap=cmap)
    ax[2].axis('off')
    ax[2].set_title(f"{image.shape[0]-1}", fontsize=14)

    fig.tight_layout()
    plt.savefig(f'{workDir}/out/{ts}_{id}_{title}.png', dpi=300)
    plt.show()
    plt.close()

# Display Single Image Helper Function
def display_single(image, title, ts, id, workDir, colorMap):
    fig, ax = plt.subplots()
    if(colorMap == "turbo"): cmap = plt.cm.turbo
    else: cmap = plt.cm.gray

    plt.title(title, fontsize=16)
    ax = plt.imshow(image, cmap=cmap)
    plt.savefig(f'{workDir}/out/{ts}_{id}_{title}.png', dpi=300)
    plt.show()
    plt.close()

# Display Triple Image Helper Function
def display_three(image, title, ts, id, workDir, colorMap):
    fig, axes = plt.subplots(nrows=1, ncols=3, sharex=True, sharey=True)
    plt.suptitle(title, fontsize=18)
    ax = axes.ravel()
    if(colorMap == "turbo"): cmap = plt.cm.turbo
    else: cmap = plt.cm.gray

    ax[0].imshow(image[0], cmap=cmap)
    ax[0].axis('off')
    ax[0].set_title("0", fontsize=14)

    half = int(np.floor(len(image) / 2))
    ax[1].imshow(image[half], cmap=cmap)
    ax[1].axis('off')
    ax[1].set_title(f"{half}", fontsize=14)

    ax[2].imshow(image[len(image)-1], cmap=cmap)
    ax[2].axis('off')
    ax[2].set_title(f"{len(image)-1}", fontsize=14)

    fig.tight_layout()
    plt.savefig(f'{workDir}/out/{ts}_{id}_{title}.png', dpi=300)
    plt.show()
    plt.close()