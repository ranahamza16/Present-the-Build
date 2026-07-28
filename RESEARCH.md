# Research Notes — Derawar Fort Reconstruction

## Research question
What reconstruction method and site-context research does the Derawar Fort COLMAP pipeline in this repo need to be historically accurate and technically sound?

## Site reference (for scale-checking the reconstruction)
Derawar Fort is located in Yazman Tehsil, Bahawalpur District, Punjab, in the Cholistan Desert. Sources place its construction around the 9th century, with major reconstruction in the 18th century under Nawab Sadeq Muhammad Khan. The fort has 40 bastions, a wall perimeter of roughly 1500 metres, and walls standing about 30 metres high.

These figures matter for this pipeline because sparse/dense point clouds from COLMAP have no inherent real-world scale — they're only accurate up to an unknown scale factor unless anchored to a known measurement. The 30m wall height and 1500m perimeter are usable as rough sanity-check references: if a reconstructed section implies wall heights wildly different from ~30m relative to its own width, that's a signal the reconstruction (or the image set) has a problem, not that the fort itself is unusual.

## Method reference (for judging image-set adequacy)
This pipeline uses COLMAP for Structure-from-Motion (sparse reconstruction) and Multi-View Stereo (dense reconstruction), following the standard pipeline: feature extraction → feature matching → sparse mapping → dense stereo. COLMAP is maintained as an open-source, BSD-licensed tool from ETH Zurich and UNC Chapel Hill, built on the "Structure-from-Motion Revisited" and companion MVS papers by Schönberger et al. (2016).

A 2026 preprint proposes a quantitative acceptance threshold for heritage photogrammetry: **Mean Track Length (MTL) between 3.60 and 4.20** indicates a reliable reconstruction, based on 66 experiments across eight types of architectural components. Below that range, geometry becomes unstable from data sparsity; above it, additional images stop improving quality and can introduce noise instead.

**Applied to this project:** the current image set pulls 19 curated images from Wikimedia Commons. Before trusting a reconstruction as accurate, MTL should be checked (COLMAP reports this in its sparse reconstruction summary/statistics) against the 3.60–4.20 range, rather than assuming 19 images is automatically sufficient.

## Citation note
If this project is formally published, the underlying SfM/MVS algorithm should be credited to its original source (Schönberger & Frahm, via the COLMAP maintainer page at demuc.de/colmap), not just referenced generically as "COLMAP."

## What I personally checked / changed
[PASTE YOUR REAL NUMBER HERE — e.g. "I ran colmap model_analyzer on my sparse reconstruction and got a Mean Track Length of X.XX, which means [PASS — my 19-image set is adequate / WARN — I likely need more images with better overlap]."]

## Sources
1. Wikipedia — Derawar Fort — https://en.wikipedia.org/wiki/Derawar_Fort
2. COLMAP official documentation — https://colmap.readthedocs.io/en/latest/
3. COLMAP maintainer page (citation source) — https://demuc.de/colmap/
4. Mean Track Length framework for heritage photogrammetry (preprint, Feb 2026) — https://www.researchsquare.com/article/rs-8709145/v1
5. COLMAP official GitHub repository — https://github.com/colmap/colmap
