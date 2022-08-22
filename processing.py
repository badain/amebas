# Imports
# utilities
import numpy as np

# image processing
from skan import Skeleton
from scipy import interpolate, ndimage
from skimage import filters
from loess.loess_1d import loess_1d
from skimage.morphology import skeletonize
from skimage.measure import label, regionprops

# visualization
from matplotlib import pyplot as plt

# Thresholding
def thresholding(image, n_points, estimate, verbose, workDir, ts):
    threshold_values = []
    mask_image = np.zeros(image.shape) # binary image where foreground > thresh

    for frame in range(image.shape[0]): # for every timeframe
        threshold_values.append(filters.threshold_isodata(image[frame,:,:])) # gets threshold value for each image
        mask_image[frame,:,:] = image[frame,:,:] > threshold_values[frame]

    if(estimate):
        if(n_points > image.shape[0] or n_points < 3): n_points = 40 # exception handling
        frac = n_points / len(threshold_values)
        xout, smooth_threshold_values, wout = loess_1d(np.arange(len(threshold_values)), np.array(threshold_values), xnew=None, degree=1, frac=frac, npoints=None, rotate=False, sigy=None)

        if(verbose):
            fig, ax = plt.subplots()
            plt.title(f"LOESS smoothing frac={frac}")
            plt.plot(np.arange(len(threshold_values)), smooth_threshold_values, color="#4d6edf")
            plt.scatter(np.arange(len(threshold_values)), threshold_values, s=18, color='#31f199')
            plt.savefig(f'{workDir}/out/{ts}_2_2_1_{"loess"}.png', dpi=300)
            plt.show()
            plt.close()

        return mask_image, smooth_threshold_values

    return mask_image, threshold_values

# Isolates Object with Largest Area
def isolate_largest_area(image):
    largest_regions = []
    for frame in range(image.shape[0]): # for every timeframe
        labels = label(image[frame, :, :])
        regions = regionprops(labels)
        if(len(regions) > 1):
            largest_region = max(regions, key=lambda region: region.area)
            largest_regions.append(largest_region)
            yy = largest_region.coords[:,0]
            xx = largest_region.coords[:,1]
            image[frame,:,:] = np.zeros(image[frame,:,:].shape)
            image[frame, yy, xx] = 1
        else:
            largest_regions.append(regions[0])

    return image, largest_regions

# Apply the mask on image
def apply_mask(image, mask):
    foreground_image = image.copy() # foreground only
    background_image = image.copy() # background only

    for frame in range(image.shape[0]): # for every timeframe
        foreground_image[frame,:,:] = background_image[frame,:,:] * mask[frame,:,:]       # foreground masking
        background_image[frame,:,:] = background_image[frame,:,:] * (1 - mask[frame,:,:]) # background masking

    return foreground_image, background_image

def masked_foreground(image, mask):
    for frame in range(image.shape[0]): # for every timeframe
        image[frame,:,:] = image[frame,:,:] * mask[frame,:,:] # foreground masking

    return image

# Skeletonization
def skeletonize_all_frames(image):
    skeleton_timelapse = np.zeros(image.shape)

    for frame in range(image.shape[0]):
        skeleton_timelapse[frame,:,:] = skeletonize(image[frame,:,:], method='lee')

    return skeleton_timelapse

def skeletonization(image):
    skeleton = skeletonize(image, method='lee')

    return skeleton, Skeleton(skeleton)

# Gets direction information from skeletons
def get_growth_direction(first_skeleton_object, last_skeleton_object):

    # get the distance between endpoints: defines grow direction
    end_points_first = np.array(first_skeleton_object.coordinates[first_skeleton_object.degrees == 1].tolist())
    end_points_last = np.array(last_skeleton_object.coordinates[last_skeleton_object.degrees == 1].tolist())

    dist_0 = np.linalg.norm(end_points_last[0]-end_points_first[0])
    dist_1 = np.linalg.norm(end_points_last[1]-end_points_first[1])

    if(dist_0 < dist_1): # lesser is the start point, must be the first element in the last_skeleton_object coordinates array
        coordinates = last_skeleton_object.coordinates[1:] # removes skans 0 index
    else:
        coordinates = last_skeleton_object.coordinates[1:] # removes skans 0 index
        coordinates = coordinates[::-1] # reverse array

    # get vector angle: defines if growth is vertical or horizontal
    delta = end_points_last[0] - end_points_last[-1] # vector given by the skeletons endpoints
    angle = np.arctan2(delta[0], delta[-1]) # angle of the vector [-π, π]
    angle = (np.degrees(angle) % 180) # angle in range [0, π]

    x, y = coordinates.T # transpose, then unpack  [vertical, horizontal]
    if(angle <= 45 or angle >= 135):
        if(y[y.shape[0]-1] - y[0] >= 0): growing_forward = True
        else: growing_forward = False
    elif(angle > 45 and angle < 135):
        if(x[x.shape[0]-1] - x[0] >= 0): growing_forward = True
        else: growing_forward = False

    return angle, coordinates, growing_forward

# Extrapolate Skeleton based on the direction
def extrapolate(skeleton, interpolation_size, extension, angle, coordinates):
    x, y = coordinates.T # transpose, then unpack  [vertical, horizontal]

    # extract points from the growing tip
    x_cut = x[-interpolation_size:] # vertical
    y_cut = y[-interpolation_size:] # horizontal


    # linear interpolation
    edges_x = [x_cut[0], x_cut[-1]] # vertical
    edges_y = [y_cut[0], y_cut[-1]] # horizontal
    if(angle <= 45 or angle >= 135): f = interpolate.interp1d(edges_y, edges_x, kind='linear', fill_value='extrapolate') # generates extrapolation function for horizontal growth
    elif(angle > 45 and angle < 135): f = interpolate.interp1d(edges_x, edges_y, kind='linear', fill_value='extrapolate') # generates extrapolation function for vertical growth

    extrapolation = np.zeros(skeleton.shape)
    if(angle <= 45 or angle >= 135):
        skeleton_tip = int(y[y.shape[0]-1])
        if(y[y.shape[0]-1] - y[0] >= 0): growing_forward = True
        else: growing_forward = False
    elif(angle > 45 and angle < 135):
        skeleton_tip = int(x[x.shape[0]-1])
        if(x[x.shape[0]-1] - x[0] >= 0): growing_forward = True
        else: growing_forward = False

    if(growing_forward):
        if(extension == -1): extension = (skeleton.shape[0] - skeleton_tip) - 1 # extends to edge [skeleton_tip -> image.shape]
        for i in range(skeleton_tip+1, skeleton_tip+extension): # extends [extension] pixels from skeleton tip in `forward` direction
            if(int(f(i)) < extrapolation.shape[1]): extrapolation[i, int(f(i))] = 1
            else: break
    else:
        if(extension == -1): extension = skeleton_tip # extends to edge [0 -> skeleton_tip]
        for i in range(skeleton_tip-extension, skeleton_tip): # extends [extension] pixels from skeleton tip in 'backward' direction
            if(int(f(i)) >= 0 and int(f(i)) < extrapolation.shape[1]): extrapolation[int(f(i)), i] = 1
            else: break

    return extrapolation

# creates gaussian kernel with side length `l` and a sigma of `sig`
# https://stackoverflow.com/a/43346070
def gkern(l, sig):
    ax = np.linspace(-(l - 1) / 2., (l - 1) / 2., l)
    gauss = np.exp(-0.5 * np.square(ax) / np.square(sig))
    kernel = np.outer(gauss, gauss)
    return kernel / np.sum(kernel)

# generates kymograph
def kymograph(image, coordinates, kernel_size, growing_forward):
    kernel = gkern(kernel_size, 1) # default: 3x3 gaussian kernel

    coordinates = coordinates[1:] # removes skans 0 index
    kymograph = np.zeros((image.shape[0], coordinates.shape[0])) # shape is last skeleton size (horizontal) and number of frames (vertical)

    for frame in range(image.shape[0]): # for each frame
        gaussian = ndimage.convolve(image[frame,:,:], kernel, mode='nearest', cval=0.0) # convolves image and 3x3 gaussian kernel
        if growing_forward:
            for idx_x, coordinate in enumerate(coordinates): # iterates skeleton
                kymograph[frame, idx_x] = (gaussian[int(coordinate[0]), int(coordinate[1])])
        else:
            for idx_x, coordinate in enumerate(reversed(coordinates)): # iterates reversed skeleton
                kymograph[frame, idx_x] = (gaussian[int(coordinate[0]), int(coordinate[1])])

    return kymograph

# generates ratiometric images
def ratiometric(channel_0, channel_1, signal_c_1, mask_c_1, thresh_c_1, smooth_ratio, verbose, switch_ratio):
    ratio = np.zeros(channel_0.shape)
    masked_ratio = []

    for frame in range(channel_0.shape[0]): # for each frame

        # background threshold subtraction
        if(switch_ratio):
            c_0_cleaned = channel_1[frame,:,:] - thresh_c_1[frame]
            c_1_cleaned = channel_0[frame,:,:] - thresh_c_1[frame]
        else:
            c_0_cleaned = channel_0[frame,:,:] - thresh_c_1[frame]
            c_1_cleaned = channel_1[frame,:,:] - thresh_c_1[frame]

        # ratio
        ratio[frame,:,:] = np.divide(c_1_cleaned, c_0_cleaned, out=np.zeros(c_1_cleaned.shape, dtype=float), where=c_0_cleaned!=0)
        del c_0_cleaned # decrease ref counter
        del c_1_cleaned # decrease ref counter

        # signal data extraction
        signal_data = []
        yy = signal_c_1[frame].coords[:,0]
        xx = signal_c_1[frame].coords[:,1]
        for y, x in zip(yy, xx):
            signal_data.append(ratio[frame, y, x])

        # IQR whiskers evaluation
        q75, q25 = np.percentile(signal_data, [75 ,25])
        iqr = q75 - q25
        upper_whisker = q75 + (1.5 * iqr)

        for y, x in zip(yy, xx):
            # rejects upper outliers
            if (ratio[frame, y, x] > upper_whisker):
                # evaluates neighborhood median
                median = []
                for i in range(-1,2):
                    for j in range(-1,2):
                        if(y+i >= 0 and y+i < ratio[frame, :, :].shape[0] and x+j >= 0 and x+j < ratio[frame, :, :].shape[1]): # exception handling
                            if(ratio[frame, y+i, x+j] != 'masked'): median.append(ratio[frame, y+i, x+j])
                # checks neighborhood existence
                if(len(median) == 0): ratio[frame, y, x] = upper_whisker # saturates
                else:
                    q50 = np.percentile(median, [50])
                    ratio[frame, y, x] = q50 # replaces with median

        if(smooth_ratio): masked_ratio.append(np.ma.array(filters.median(ratio[frame,:,:]), mask = 1-mask_c_1[frame, :, :]))
        else: masked_ratio.append(np.ma.array(ratio[frame,:,:], mask = 1-mask_c_1[frame, :, :]))

    return ratio, masked_ratio