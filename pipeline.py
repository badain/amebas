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
    # [1] Timelapse Input
    parser.add_argument('filename', type=str, metavar='filename', help='Input timelapse filename. May be a .dv or a .tiff file.')
    parser.add_argument("--v", "--verbose", default=False, action='store_true', help='Outputs internal steps of the pipeline.')
    # [2] Single-Cell Segmentation
    parser.add_argument("--s", "--sigma", type=int, nargs="?", default=2, help='Sigma used in the Gaussian Filter preprocessing step in preparation to the cell segmentation. Default is 2.')
    # [3] Midline Tracing
    parser.add_argument("--a", "--complete_skeletonization", default=False, action='store_true', help='Traces the midline for each frame of the timelapse. By default, skeletonizes only the last frame.')
    parser.add_argument("--f", "--interpolation_fraction", type=float, nargs="?", default=.25, help='Fraction of the skeleton used for interpolation. Must be float contained in [0,1]. Default is 0.25.')
    parser.add_argument("--e", "--extrapolation_length", type=int, nargs="?", default=-1, help='Length in pixels of the extrapolated skeleton. Extrapolates to the edge of the image by default.')
    # [4] Kymograph Generation
    parser.add_argument("--sf", "--shift_fraction", type=float, nargs="?", default=.7, help='Fraction of the color range that will be shifted to the background in non-extrapolated kymographs. Default is 0.7.')
    parser.add_argument("--k", "--kymograph_kernel", type=int, nargs="?", default=3, help='Size of the kernel used in the kymograph Gaussian filtering. Default is 3.')
    # [5] Ratiometric Timelapse Generation
    parser.add_argument("--eb", "--estimate_bg_threshold_intensity", default=False, action='store_true', help='Estimates global background threshold intensity via loess polynomial regression of the frame-specific background threshold intensities. Default is false.')
    parser.add_argument("--n", "--n_points", type=int, nargs="?", default=40, help='Number of points used in loess smoothing of the background threshold values. Used only with --eb. Default is 40.')
    parser.add_argument("--r", "--switch_ratio", default=False, action='store_true', help='Switches channels used as numerator and denominator during ratio calculations. By default the second channel is the numerator and the first is the denominator.')
    parser.add_argument("--sm", "--smooth_ratio", default=False, action='store_true', help='Smooths ratiometric output by applying a Median Filter pass. Default is false.')
    parser.add_argument("--o", "--reject_outliers", default=False, action='store_true', help='During the ratiometric timelapse generation, rejects pixels with abnormal intensities and replaces with the local average. Default is false.')
    parser.add_argument("--b", "--background_ratio", default=False, action='store_true', help='Export background in the ratiometric output. By default, replaces background with zeros.')
    
    args = parser.parse_args()

    # 1 FILE READING
    workDir = "./"
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
    if(args.v): display(c_1, 'input', args.filename, '1', workDir, 'turbo')

    # 2 DETECTING THE MAIN CELL
    print('[2] main cell segmentation')
    print('[2.1] preprocessing filters')
    if(hasTwoChannels): median_c_0 = filters.median(c_0)
    median_c_1 = filters.median(c_1)
    gaussian_c_1 = filters.gaussian(median_c_1, sigma=args.s)
    if(args.v): display(gaussian_c_1, 'filters', args.filename, '2_1', workDir, 'turbo')
    print('[2.2] isodata thresholding')
    mask_c_1, thresh_c_1 = thresholding(gaussian_c_1, args.n, args.eb, args.v, '.', args.filename)
    if(args.v): display(mask_c_1, 'thresholding', args.filename, '2_2', workDir, 'gray')
    np.savetxt(f"{args.filename}_background_treshold_c_1.csv", thresh_c_1, delimiter=",")

    # isolating largest area
    print('[2.3] isolating region with largest area')
    mask_c_1, signal_c_1 = isolate_largest_area(mask_c_1)
    if(args.v): display(mask_c_1, 'isolation', args.filename, '2_3', workDir, 'gray')
    io.imsave(f'{args.filename}_binary_mask.tiff', mask_c_1) # exports binary mask timelapse

    # 3 SKELETONIZE
    last_frame = c_1.shape[0] - 1
    print("[3.1] skeletonization")
    if(args.a):
        skeleton_timelapse, skeleton_coordinates = skeletonize_all_frames(mask_c_1)    # skeletonizes all frames
        io.imsave(f'{args.filename}_skeletonized.tiff', skeleton_timelapse) # exports skeleton timelapse
        skeleton, skeleton_object = skeleton_timelapse[last_frame], skeleton_coordinates[last_frame]
        first_skeleton, first_skeleton_object = skeleton_timelapse[0], skeleton_coordinates[0]
    else:
        skeleton, skeleton_object = skeletonization(mask_c_1[last_frame,:,:])
        first_skeleton, first_skeleton_object = skeletonization(mask_c_1[0,:,:])
        io.imsave(f'{args.filename}_skeletonized.tiff', skeleton)
    if(args.v): display_single(skeleton, 'skeletonize', args.filename, '3_1', workDir, 'gray')

    angle, coordinates, growing_forward = get_growth_direction(first_skeleton_object, skeleton_object)
    if(not args.a):
        print("[3.2] skeleton extrapolation")
        if(args.f > 0):
            if(args.f >= 1): interpolation_size = coordinates.shape[0] - 1
            else: interpolation_size = int(coordinates.shape[0] * args.f)
            extrapolation = extrapolate(skeleton, interpolation_size, args.e, angle, coordinates)
            extended_skeleton = Skeleton(np.logical_or(skeleton, extrapolation)) # extrapolation + skeleton
            if(args.v): display_single(np.logical_or(skeleton, extrapolation), 'extrapolate', args.filename, '3_2', workDir, 'gray')
        else:
            extended_skeleton = skeleton_object

    # 4 KYMOGRAPH
    print("[4] kymograph generation")
    shifted_turbo_cmap = generate_cmap(args.sf)
    if(not args.a):
        kymograph_c_1 = kymograph(median_c_1, extended_skeleton.coordinates, args.k, growing_forward)
        if(hasTwoChannels): kymograph_c_0 = kymograph(median_c_0, extended_skeleton.coordinates, args.k, growing_forward)
    else:
        kymograph_c_1 = kymograph_framewise(median_c_1, skeleton_coordinates, args.k, growing_forward)
        if(hasTwoChannels): kymograph_c_0 = kymograph_framewise(median_c_0, skeleton_coordinates, args.k, growing_forward)

    # output
    if(not args.a): cmap = plt.cm.turbo
    else: cmap = shifted_turbo_cmap

    if(args.v): display_single(kymograph_c_1, 'kymograph', args.filename, '4', workDir, 'turbo')
    plt.imsave(f'{args.filename}_kymograph_c_1.png', kymograph_c_1, cmap=cmap)
    np.savetxt(f"{args.filename}_kymograph_c_1.csv", kymograph_c_1, delimiter=",")
    if(hasTwoChannels):
        plt.imsave(f'{args.filename}_kymograph_c_0.png', kymograph_c_0, cmap=cmap)
        np.savetxt(f"{args.filename}_kymograph_c_0.csv", kymograph_c_0, delimiter=",")

    # 5 RATIOMETRIC IMAGE
    print("[5] ratiometric results")
    if(hasTwoChannels):
        ratio, masked_ratio = ratiometric(median_c_0, median_c_1, signal_c_1, mask_c_1, thresh_c_1, args.sm, args.o, args.r)
        if(args.b): io.imsave(f'{args.filename}_ratiometric.tiff', ratio)
        else: io.imsave(f'{args.filename}_ratiometric.tiff', masked_foreground(ratio, mask_c_1))

        if(not args.a): kymograph_ratio = kymograph(masked_foreground(ratio, mask_c_1), skeleton_object.coordinates, args.k, growing_forward)
        else: kymograph_ratio = kymograph_framewise(masked_foreground(ratio, mask_c_1), skeleton_coordinates, args.k, growing_forward)

        plt.imsave(f'{args.filename}_kymograph_ratio.png', kymograph_ratio, cmap=shifted_turbo_cmap)
        np.savetxt(f"{args.filename}_kymograph_ratio.csv", kymograph_ratio, delimiter=",")