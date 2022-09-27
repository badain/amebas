# AMEBaS
## Automatic Midline Extraction and Background Subtraction

<p align="center">
  <img  src="https://raw.githubusercontent.com/badain/amebas/main/amebas_banner.gif">
  <img  src="https://raw.githubusercontent.com/badain/amebas/main/pipeline_banner.png">
</p>

---------------------------------------

## Description
Cell polarity is a macroscopic phenomenon established by a collection of spatially concentrated molecules and structures that culminate in the emergence of specialized morphological domains at the subcellular level. It is associated with the development of asymmetric morphological structures that underlies key biological functions such as cell division and migration. In addition, disruption of cell polarity has been linked to epithelial tissue-related disorders such as cancer and gastric dysplasia.

Current methods to evaluate the spatial-temporal dynamics of fluorescent reporters in individual polarized cells often involve manual steps to trace a midline along the cells’ major axis, which is time-consuming and prone to strong annotation biases. Furthermore, although ratiometric analysis can correct the uneven distribution of reporter molecules using two fluorescence channels, background subtraction techniques are frequently arbitrary and lack statistical support.

Here we introduce a novel computational pipeline to automate and quantify the spatiotemporal behavior of single cells using a model of cell polarity: pollen tube growth and cytosolic ion dynamics. A three-step algorithm was developed to process ratiometric images and extract a quantitative representation of intracellular dynamics and growth. The first step segments the cell from the background, producing a binary mask by a thresholding technique in the pixel intensity space. The second step traces a path through the midline of the cell through a skeletonization morphological operation. Finally, the third step provides the processed data as a ratiometric timelapse and yields a ratiometric kymograph (i.e. a 1D spatial profile through time). Data from ratiometric images acquired with genetically encoded fluorescent reporters from growing pollen tubes were used to benchmark the method. This pipeline allows for faster, less biased, and more accurate representation of the spatiotemporal dynamics along the midline of polarized cells, thus, advancing the quantitative toolkit available to investigate cell polarity.

## Using AMEBaS
AMEBaS can be used as a Colab code or as a command line program

### Colab
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/badain/amebas/blob/main/AMEBAS_Colab.ipynb)

AMEBaS Colab features a pre-processed sample data timelapse


### Command Line
usage:
```
pipeline.py [-h] [--a] [--s [S]] [--f [F]] [--e [E]] [--n [N]] [--v] [--r] [--sm] [--eb] [--o] [--b] [--k [K]] filename
```

positional arguments:
```
  filename              Input timelapse filename. May be a .dv or a .tiff file.
```

optional arguments:
```
  -h, --help            show this help message and exit
  --v, --verbose        Outputs internal steps of the pipeline.
  --s [S], --sigma [S]  Sigma used in the Gaussian Filter preprocessing step in preparation to the cell segmentation. Default is 2.
  --a, --complete_skeletonization
                        Traces the midline for each frame of the timelapse. By default, skeletonizes only the last frame.
  --f [F], --interpolation_fraction [F]
                        Fraction of the skeleton used for interpolation. Must be float contained in [0,1]. Default is 0.25.
  --e [E], --extrapolation_length [E]
                        Length in pixels of the extrapolated skeleton. Extrapolates to the edge of the image by default.
  --sf [SF], --shift_fraction [SF]
                        Fraction of the color range that will be shifted to the background in non-extrapolated kymographs. Default is 0.7.
  --k [K], --kymograph_kernel [K]
                        Size of the kernel used in the kymograph Gaussian filtering. Default is 3.
  --eb, --estimate_bg_threshold_intensity
                        Estimates global background threshold intensity via loess polynomial regression of the frame-specific background threshold intensities. Default is false.
  --n [N], --n_points [N]
                        Number of points used in loess smoothing of the background threshold values. Used only with --eb. Default is 40.
  --r, --switch_ratio   Switches channels used as numerator and denominator during ratio calculations. By default the second channel is the numerator and the first is the denominator.
  --sm, --smooth_ratio  Smooths ratiometric output by applying a Median Filter pass. Default is false.
  --o, --reject_outliers
                        During the ratiometric timelapse generation, rejects pixels with abnormal intensities and replaces with the local average. Default is false.
  --b, --background_ratio
                        Export background in the ratiometric output. By default, replaces background with zeros.
```