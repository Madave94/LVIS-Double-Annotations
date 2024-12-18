# LVIS-5000

This repository contains a subset of 5,000 doubly annotated images from the LVIS dataset [[1]](#1), used for evaluating annotation
consistency. It includes the original annotations provided by Ross Girshick and a modified set that aligns with the 
LVIS 1.0 class definitions.

The annotations are further used in a WACV publication [[2]](#2) analyzing the Convergence Threshold of object recognition models.

## What does this do?

1. Load the v0.5 double annotations and the v1.0 single annotations using validation subset.
2. Find the mapping from the 1723 classes in v0.5 to the final 1203 classes in v1.0.
3. Ensure that image_ids and annotation_ids between the double annotations don't overlap.
4. Add generic rater identification to annotations and image.

## How to use it?

**[Download the double annotations here.](processed_double_annos_v1.0/lvis_v1.0_val_doubly_annos.json)** They are in the folder 
`processed_double_annos_v1.0`. The **corresponding images** for the double annotated data are the
[COCO 2017 Val images](https://cocodataset.org/#download).

The script is just here for reproducability, in order to run it you will need to download the 
[validation annotations](https://www.lvisdataset.org/dataset), rename them to `lvis_v1.0_val.json` and put them into the
folder `original_annos_v1.0`. Then the processing script can be run from the project root `python processing_script.py`.

## Reference

<a id="1">[1]</a> Gupta Agrim, Piotr Dollar, and Ross Girshick. "Lvis: A dataset for large vocabulary instance segmentation." 
_Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)_. 2019. 
[Link](https://openaccess.thecvf.com/content_CVPR_2019/html/Gupta_LVIS_A_Dataset_for_Large_Vocabulary_Instance_Segmentation_CVPR_2019_paper.html)

<a id="2">[2]</a> Tschirschwitz David and Rodehorst Volker . "Label Convergence: Defining an Upper Performance Bound in 
Object Recognition through Contradictory Annotations" _Proceedings of the IEEE/CVF Winter Conference on Applications of 
Computer Vision (WACV)_. 2025. [Link](https://arxiv.org/abs/2409.09412)
