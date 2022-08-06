# AMEBaS
## Automatic Midline Extraction and Background Subtraction

<p align="center">
  <img  src="https://raw.githubusercontent.com/badain/amebas/main/pipeline_banner.jpg">
</p>

---------------------------------------

## Description
Cell polarity is a macroscopic phenomenon established by a collection of spatially concentrated molecules and structures that culminate in the emergence of specialized morphological domains at the subcellular level. It is associated with the development of asymmetric morphological structures that underlies key biological functions such as cell division and migration. In addition, disruption of cell polarity has been linked to epithelial tissue-related disorders such as cancer and gastric dysplasia.

Current methods to evaluate the spatial-temporal dynamics of fluorescent reporters in individual polarized cells often involve manual steps to trace a midline along the cells’ major axis, which is time-consuming and prone to strong biases. Furthermore, although ratiometric analysis can correct the uneven distribution of reporter molecules using two fluorescence channels, background subtraction techniques are frequently arbitrary and lack statistical support.

Here we introduce a novel computational pipeline to automate and quantify the spatiotemporal behavior of single cells using a model of cell polarity: pollen tube growth and cytosolic ion dynamics. A three-step algorithm was developed to process ratiometric images and extract a quantitative representation of intracellular dynamics and growth. The first step segments the cell from the background, producing a binary mask by a thresholding technique in the pixel intensity space. The second step traces a path through the midline of the cell through skeletonization. Finally, the third step provides the processed data as a ratiometric timelapse and yields a ratiometric kymograph (i.e. 1D spatial profile through time). Data from ratiometric images acquired with genetically encoded fluorescent reporters from growing pollen tubes were used to benchmark the method. This pipeline allows faster, less biased and more accurate representation of the spatiotemporal dynamics along the midline of polarized cells, thus, advancing the quantitative toolkit available to investigate cell polarity.

## Using AMEBaS
 [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/badain/amebas/blob/main/AMEBAS_Colab.ipynb)

usage: pipeline.py [-h] [--s [S]] [--f [F]] [--e [E]] [--n [N]] [--v] [--r] [--sm] [--b] [--k [K]] filename

AMEBaS: Automatic Midline Extraction and Background Subtraction

positional arguments:
  filename              dv or tiff filename

optional arguments:
  -h, --help            show this help message and exit
  --s [S], --sigma [S]  sigma used in pre-processing steps for thresholding
  --f [F], --interpolation_fraction [F]
                        fraction of the skeleton used for interpolation
  --e [E], --extrapolation_length [E]
                        length of the extrapolated skeleton
  --n [N], --n_points [N]
                        number of points used in loess smoothing of the background threshold values
  --v, --verbose        outputs every step in the pipeline
  --r, --switch_ratio   switches channels used as numerator and denominator during ratio calculations
  --sm, --smooth_ratio  smooths ratiometric output
  --b, --background_ratio
                        export background in ratiometric output. if false, replaces background with zeros.
  --k [K], --kymograph_kernel [K]
                        size of the kernel used in the kymograph gaussian filtering