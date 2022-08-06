# AMEBaS
## Automatic Midline Extraction and Background Subtraction

<p align="center">
  <img  src="https://raw.githubusercontent.com/badain/amebas/main/pipeline_banner.jpg">
</p>

---------------------------------------

Cell polarity is a macroscopic phenomenon established by a collection of spatially concentrated molecules and structures that culminate in the emergence of specialized morphological domains at the subcellular level. It is associated with the development of asymmetric morphological structures that underlies key biological functions such as cell division and migration. In addition, disruption of cell polarity has been linked to epithelial tissue-related disorders such as cancer and gastric dysplasia.

Current methods to evaluate the spatial-temporal dynamics of fluorescent reporters in individual polarized cells often involve manual steps to trace a midline along the cells’ major axis, which is time-consuming and prone to strong biases. Furthermore, although ratiometric analysis can correct the uneven distribution of reporter molecules using two fluorescence channels, background subtraction techniques are frequently arbitrary and lack statistical support.

Here we introduce a novel computational pipeline to automate and quantify the spatiotemporal behavior of single cells using a model of cell polarity: pollen tube growth and cytosolic ion dynamics. A three-step algorithm was developed to process ratiometric images and extract a quantitative representation of intracellular dynamics and growth. The first step segments the cell from the background, producing a binary mask by a thresholding technique in the pixel intensity space. The second step traces a path through the midline of the cell through skeletonization. Finally, the third step provides frame-wise background estimates and yields a ratiometric kymograph (i.e. 1D spatial profile through time). Data from ratiometric images acquired with genetically encoded fluorescent reporters from growing pollen tubes were used to benchmark the method. This pipeline allows faster, less biased and more accurate representation of the spatiotemporal dynamics along the midline of polarized cells, thus, advancing the quantitative toolkit available to investigate cell polarity.