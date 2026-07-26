# Derawar Fort COLMAP Pipeline Research

**Research Question:** What reconstruction method and site-context research does the Derawar Fort COLMAP pipeline in Present-the-Build need to be historically accurate and technically sound?

## Site-Context & Scale Reference
Derawar Fort is a massive square fortress located in the Cholistan Desert. Its brick walls have a circumference of 1,500 meters and stand up to 30 meters high. Forty circular bastions, ten on each side, support the massive structure. 

These monumental dimensions (1,500m circumference, 30m height) serve as a crucial **scale-check reference**. By validating our point clouds and meshes against these real-world measurements, we can ensure the final 3D reconstruction remains true to its historical and physical footprint.

## Image Acquisition Acceptance Criterion
To ensure we have a sufficient number of images for a stable reconstruction without capturing excessive redundancy, we will use the **Mean Track Length (MTL)** metric as our core acceptance criterion. 

According to recent photogrammetry frameworks, a reliable reconstruction is achieved when the MTL value falls within the optimal range of **3.60 to 4.20**:
- **MTL < 3.60**: Indicates data sparsity, leading to unstable geometry and reconstruction failure.
- **MTL > 4.20**: Does not improve reconstruction quality; instead, it introduces noise and incurs unnecessary computational costs.
