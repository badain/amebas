# utilities
import time
import argparse
import numpy as np

# image processing
from mrc import imread # dv reader
from skan import Skeleton
from skimage import io, filters

# visualization
from matplotlib import pyplot as plt

# repository
from visualization import *
from processing import *

if __name__ == "__main__":
    # execution time
    ts = time.time()
    print(f'[timestamp] {ts}')

    # Argument Parsing
    parser = argparse.ArgumentParser(description='AMEBaS: Automatic Midline Extraction and Background Subtraction')
    parser.add_argument('filename', type=str, metavar='filename', help='dv or tiff filename')
    parser.add_argument("--s", "--sigma", type=int, nargs="?", default=2, help='sigma used in pre-processing steps for thresholding')
    parser.add_argument("--f", "--interpolation_fraction", type=int, nargs="?", default=.25, help='fraction of the skeleton used for interpolation') # min 3
    parser.add_argument("--e", "--extrapolation_length", type=int, nargs="?", default=-1, help='length of the extrapolated skeleton') # min para a tip
    parser.add_argument("--n", "--n_points", type=int, nargs="?", default=40, help='number of points used in loess smoothing of the background threshold values')
    parser.add_argument("--v", "--verbose", default=False, action='store_true', help='outputs every step in the pipeline')
    parser.add_argument("--r", "--switch_ratio", default=False, action='store_true', help='switches channels used as numerator and denominator during ratio calculations') # opcao para canais codificados no nome do arquivo
    parser.add_argument("--sm", "--smooth_ratio", default=False, action='store_true', help='smooths ratiometric output')
    parser.add_argument("--b", "--background_ratio", default=True, action='store_true', help='export background in ratiometric output. if false, replaces background with zeros.')
    parser.add_argument("--k", "--kymograph_kernel", type=int, nargs="?", default=3, help='size of the kernel used in the kymograph gaussian filtering')
    args = parser.parse_args()

    # 1 FILE READING
    print('[1] file reading')
    if(".dv" in  args.filename):
        im = imread(args.filename)
    elif(".tiff" in  args.filename):
        im = np.array(io.imread(args.filename))
    elif(".tif" in  args.filename):
        im = np.array(io.imread(args.filename))
    else:
        raise Exception('Filetype not recognized.')

    # shape: num_images, channels, Y, X
    print(args.filename, "shape:", im.shape)

    # channel separation
    if(im.ndim == 4):
        hasTwoChannels = True
    elif(im.ndim == 3):
        hasTwoChannels = False
    else:
        raise Exception('Invalid number of dimensions.')

    if(hasTwoChannels):
        c_0 = im[:,0,:,:]
        c_1 = im[:,1,:,:]
    else:
        c_1 = im
    if(args.v): display(c_1, 'input', ts, '1', 'turbo')

    # 2 DETECTING THE MAIN CELL
    print('[2] main cell segmentation')
    print('[2.1] pre-processing filters')
    if(hasTwoChannels): median_c_0 = filters.median(c_0) # pre-processing step
    median_c_1 = filters.median(c_1) # pre-processing step
    gaussian_c_1 = filters.gaussian(median_c_1, sigma=args.s) # pre-processing step
    if(args.v): display(gaussian_c_1, 'filters', ts, '2_1', 'turbo')
    print('[2.2] isodata tresholding')
    mask_c_1, thresh_c_1 = thresholding(gaussian_c_1, args.n, args.v)
    if(args.v): display(mask_c_1, 'tresholding', ts, '2_2', 'gray')

    # isolating largest area
    print('[2.3] isolating region with largest area')
    mask_c_1, signal_c_1 = isolate_largest_area(mask_c_1)
    if(args.v): display(mask_c_1, 'isolation', ts, '2_3', 'gray')

    # 3 SKELETONIZE
    last_frame = c_1.shape[0] - 1
    print("[3.1] skeletonization")
    skeleton, skeleton_object = skeletonization(mask_c_1[last_frame,:,:])
    first_skeleton, first_skeleton_object = skeletonization(mask_c_1[0,:,:])
    if(args.v): display_single(skeleton, 'skeletonize', ts, '3_1', 'gray')
    plt.imsave(f'{ts}_skeleton.png', skeleton, cmap=plt.cm.gray)

    print("[3.2] skeleton extrapolation")
    angle, coordinates, growing_forward = get_growth_direction(first_skeleton_object, skeleton_object)
    if(args.f > 0):
        if(args.f >= 1): interpolation_size = coordinates.shape[0] - 1
        else: interpolation_size = coordinates.shape[0] * args.f
        extrapolation = extrapolate(skeleton, skeleton_object, int(interpolation_size), args.e, angle, coordinates)
        extended_skeleton = Skeleton(np.logical_or(skeleton, extrapolation)) # extrapolation + skeleton
        if(args.v): display_single(np.logical_or(skeleton, extrapolation), 'extrapolate', ts, '3_2', 'gray')
    else:
        extended_skeleton = skeleton_object

    # 4 KYMOGRAPH
    print("[4] kymograph generation")
    kymograph_c_1 = kymograph(median_c_1, extended_skeleton.coordinates, args.k, growing_forward)
    if(hasTwoChannels): kymograph_c_0 = kymograph(median_c_0, extended_skeleton.coordinates, args.k, growing_forward)

    # output
    if(args.v): display_single(kymograph_c_1, 'kymograph', ts, '4', 'turbo')
    plt.imsave(f'{ts}_kymograph_c_1.png', kymograph_c_1, cmap=plt.cm.turbo)
    np.savetxt(f"{ts}_kymograph_c_1.csv", kymograph_c_1, delimiter=",")
    if(hasTwoChannels):
        plt.imsave(f'{ts}_kymograph_c_0.png', kymograph_c_0, cmap=plt.cm.turbo)
        np.savetxt(f"{ts}_kymograph_c_0.csv", kymograph_c_0, delimiter=",")

    # 5 RATIOMETRIC IMAGE
    print("[5] ratiometric results")
    if(hasTwoChannels):
        ratio = ratiometric(median_c_0, median_c_1, signal_c_1, mask_c_1, thresh_c_1, args.sm, args.v, args.r)
        if(args.b): io.imsave(f'{ts}_ratiometric.tiff', ratio)
        else: io.imsave(f'{ts}_ratiometric.tiff', masked_foreground(ratio, mask_c_1))

        kymograph_ratio = kymograph(ratio, extended_skeleton.coordinates, args.k, growing_forward)
        plt.imsave(f'{ts}_kymograph_ratio.png', kymograph_ratio, cmap=plt.cm.turbo)
        np.savetxt(f"{ts}_kymograph_ratio.csv", kymograph_ratio, delimiter=",")