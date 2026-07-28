# Mentor Note

## 1. Open this first
Please review the repository in this order to follow my workflow and methodology:
1. [README.md](./README.md)
2. [RESEARCH.md](./RESEARCH.md)
3. [reconstruct.py](./reconstruct.py)

## 2. What changed across sprints
* **Sprint 1**: Fixed the Wikimedia DNS block by implementing a DNS over HTTPS (DoH) fallback. ([Commit a19d81d](https://github.com/ranahamza16/Present-the-Build/commit/a19d81d))
* **Sprint 2**: Added research grounding, including Mean Track Length (MTL) thresholds and historical fort dimensions. ([Commit 5178e68](https://github.com/ranahamza16/Present-the-Build/commit/5178e68))
* **Sprint 3 & 4**: Added automated MTL validation directly into the pipeline, and verified against real COLMAP output formats (Achieved MTL of 3.85 - PASS). ([Commit 02cb2dd](https://github.com/ranahamza16/Present-the-Build/commit/02cb2dd))
* **Sprint 5**: Polished all code, comments, and documentation for this final external review.

## 3. My role
I built and debugged this automated 3D photogrammetry pipeline as part of PMW's (PreserveMy.World) Cholistan desert heritage documentation effort.

## 4. What I personally learned
I learned that committing code isn't the same as verifying it, and that DNS-level ISP blocks need application-layer workarounds like DoH, not just retry logic.

## 5. How this connects to PMW's mission
Derawar Fort is severely at risk of erosion and neglect deep in the Cholistan desert. This automated photogrammetry pipeline is a critical first step toward capturing a preserved, measurable 3D digital record of the site before it degrades further.
