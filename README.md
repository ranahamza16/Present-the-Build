# Present-the-Build

COLMAP-based 3D reconstruction pipeline for Derawar Fort, part of PreserveMy.World.

## How to Run It

1. **Prerequisites**: Ensure you have [COLMAP](https://colmap.github.io/install.html) installed and added to your system's PATH. You also need Python 3.x and the `Pillow` library (`pip install Pillow`).
2. **Clone the repository**:
   ```bash
   git clone https://github.com/ranahamza16/Present-the-Build.git
   cd Present-the-Build
   ```
3. **Run the pipeline**:
   ```bash
   python reconstruct.py
   ```
4. **Output**: The generated sparse 3D point cloud will be saved in the `output/` directory as a `.ply` file.

## Research

Please see [RESEARCH.md](./RESEARCH.md) for our site-context research and the methodology used for this reconstruction.

## Known Limitations

* **Requires COLMAP**: You must have the COLMAP executable installed on your system for the feature extraction and mapping tasks.
* **Network Restrictions**: Tested via Google Colab since local DNS blocks Wikimedia Commons without the DoH fallback in `reconstruct.py`.
