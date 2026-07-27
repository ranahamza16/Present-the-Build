# -*- coding: utf-8 -*-
"""
Derawar Fort 3D Sparse Reconstruction Pipeline
===============================================
COLMAP 4.1.0 (no-CUDA build), CPU-only.

Steps:
  1. Download curated images from Wikimedia Commons into ./images/
  2. Run COLMAP feature_extractor   (CPU-only)  -- --FeatureExtraction.use_gpu 0
  3. Run COLMAP exhaustive_matcher  (CPU-only)
  4. Run COLMAP mapper               (CPU-only)
  5. Export sparse model -> ./output/derawar_fort_reconstruction.ply
  6. Validate .ply vertex count > 0
  7. Print summary
"""

import io
import os
import sys
import time
import subprocess
import struct
import urllib.request
import urllib.error
import shutil
import json
import subprocess
import re

def resolve_via_doh(hostname):
    """Resolve hostname using Cloudflare DNS over HTTPS."""
    url = f"https://1.1.1.1/dns-query?name={hostname}&type=A"
    req = urllib.request.Request(url, headers={"Accept": "application/dns-json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        for answer in data.get("Answer", []):
            if answer.get("type") == 1:  # A record
                return answer.get("data")
    raise ValueError(f"Could not resolve {hostname} via DoH")

# Force UTF-8 output on Windows terminals
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace", line_buffering=True)

# ===========================================================================
# Paths
# ===========================================================================
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
IMAGES_DIR   = os.path.join(PROJECT_ROOT, "images")
IMAGES_RESIZED_DIR = os.path.join(PROJECT_ROOT, "images_resized")
DB_PATH      = os.path.join(PROJECT_ROOT, "colmap.db")
SPARSE_DIR   = os.path.join(PROJECT_ROOT, "sparse")
OUTPUT_DIR   = os.path.join(PROJECT_ROOT, "output")
PLY_PATH     = os.path.join(OUTPUT_DIR, "derawar_fort_reconstruction.ply")
COLMAP_EXE   = os.environ.get("COLMAP_EXE", "colmap")

# ===========================================================================
# Curated image list
# ===========================================================================
# Strategy: Focus on the EASTERN WALL / BASTION COMPLEX of Derawar Fort.
# All images show the outer face of the eastern wall and adjoining bastions
# from slightly different angles for 60-70%+ visual overlap.
# NO aerial or interior shots.
#
# URLs verified via Wikimedia Commons API (iiprop=thumburl, iiurlwidth=1200).
# The exact hash-path thumbnail URLs come directly from the API response.

IMAGES = [
    # --- Eastern wall (same photographer session: pageid 72377xxx) ---
    {
        "url":      "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Eastern_side_-_Derawar_Fort.jpg/1280px-Eastern_side_-_Derawar_Fort.jpg",
        "filename": "01_eastern_side.jpg",
    },
    {
        "url":      "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Art_work_on_eastern_wall_-_Derawar_Fort.jpg/1280px-Art_work_on_eastern_wall_-_Derawar_Fort.jpg",
        "filename": "02_art_work_eastern_wall.jpg",
    },
    {
        "url":      "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/North_wall_-_Derawar_Fort.jpg/1280px-North_wall_-_Derawar_Fort.jpg",
        "filename": "03_north_wall.jpg",
    },
    # --- Outer perimeter bastions (Bahawalpur I & II -- same session) ---
    {
        "url":      "https://upload.wikimedia.org/wikipedia/commons/thumb/0/00/Derawar_Fort%2C_Bahawalpur_I.jpg/1280px-Derawar_Fort%2C_Bahawalpur_I.jpg",
        "filename": "04_bahawalpur_I.jpg",
    },
    {
        "url":      "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Derawar_Fort%2C_Bahawalpur_II.jpg/1280px-Derawar_Fort%2C_Bahawalpur_II.jpg",
        "filename": "05_bahawalpur_II.jpg",
    },
    # --- Outer wall shots ---
    {
        "url":      "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5b/Derawar_Fort_outer_view.jpg/1280px-Derawar_Fort_outer_view.jpg",
        "filename": "06_outer_view.jpg",
    },
    {
        "url":      "https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Defense_wall_of_Nawab%27s_Fort_-_Derawar_Fort.jpg/1280px-Defense_wall_of_Nawab%27s_Fort_-_Derawar_Fort.jpg",
        "filename": "07_defense_wall.jpg",
    },
    # --- Entrance gate ---
    {
        "url":      "https://upload.wikimedia.org/wikipedia/commons/thumb/0/02/Derawar_Entrance_Gate.jpg/1280px-Derawar_Entrance_Gate.jpg",
        "filename": "08_entrance_gate.jpg",
    },
    {
        "url":      "https://upload.wikimedia.org/wikipedia/commons/thumb/7/73/Derawar_Fort_View.jpg/1280px-Derawar_Fort_View.jpg",
        "filename": "09_fort_view.jpg",
    },
    # --- Exterior medium/wide shots ---
    {
        "url":      "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Derawar_Fort_2.jpg/1280px-Derawar_Fort_2.jpg",
        "filename": "10_fort_2.jpg",
    },
    {
        "url":      "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/Guards_Tower_I_reckon_-_Derawar_Fort.jpg/1280px-Guards_Tower_I_reckon_-_Derawar_Fort.jpg",
        "filename": "11_guards_tower.jpg",
    },
    {
        "url":      "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/Derawar_Fort_side_view.jpg/1280px-Derawar_Fort_side_view.jpg",
        "filename": "12_side_view.jpg",
    },
    # --- Small originals (no thumbnail larger than original) ---
    {
        "url":      "https://upload.wikimedia.org/wikipedia/commons/b/ba/Mighty_derawar_fort.jpg",
        "filename": "13_mighty_derawar.jpg",
    },
    {
        "url":      "https://upload.wikimedia.org/wikipedia/commons/8/81/Derawar_Fort_-_Bahawalpur.jpg",
        "filename": "14_derawar_bahawalpur.jpg",
    },
    {
        "url":      "https://upload.wikimedia.org/wikipedia/commons/f/fa/Outside_Derawar_Fort.jpg",
        "filename": "15_outside_derawar.jpg",
    },
    {
        "url":      "https://upload.wikimedia.org/wikipedia/commons/thumb/7/79/The_Mighty_Derawar_Fort.jpg/1280px-The_Mighty_Derawar_Fort.jpg",
        "filename": "16_the_mighty.jpg",
    },
    {
        "url":      "https://upload.wikimedia.org/wikipedia/commons/thumb/3/39/Derawar_Fort%2C_Cholistan%2C_Bahawalpur.jpg/1280px-Derawar_Fort%2C_Cholistan%2C_Bahawalpur.jpg",
        "filename": "17_cholistan.jpg",
    },
    {
        "url":      "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/View_of_Derawar_Fort_from_East.jpg/1280px-View_of_Derawar_Fort_from_East.jpg",
        "filename": "18_view_from_east.jpg",
    },
    # --- Extra shot: different perspective ---
    {
        "url":      "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Derawar_Fort_by_M_Ali_Mir_01.jpg/1280px-Derawar_Fort_by_M_Ali_Mir_01.jpg",
        "filename": "19_m_ali_mir.jpg",
    },
]


# ===========================================================================
# Helpers
# ===========================================================================

def banner(msg):
    print("\n" + "=" * 70)
    print("  " + msg)
    print("=" * 70)


def run(cmd, label):
    """Run a subprocess, streaming output. Raises on non-zero exit."""
    banner(label)
    print("CMD: " + " ".join(cmd))
    t0 = time.time()
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    )
    for line in proc.stdout:
        print(line, end="")
    proc.wait()
    elapsed = time.time() - t0
    if proc.returncode != 0:
        print("\n[ERROR] '{}' exited with code {}".format(label, proc.returncode))
        raise RuntimeError("COLMAP step failed: " + label)
    print("\n[OK] '{}' completed in {:.1f}s".format(label, elapsed))
    return elapsed


import socket
import urllib.parse
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

def download_with_retry(url, dest_path, max_retries=5):
    """Download a URL to dest_path with exponential backoff retry on 429/5xx."""
    headers = {
        "User-Agent": "DerawarFort-3D-Pipeline/1.0 (heritage-preservation-research) Python/urllib"
    }
    
    parsed_url = urllib.parse.urlparse(url)
    hostname = parsed_url.hostname
    
    try:
        ip = socket.gethostbyname(hostname)
        print(f"      [DNS] Resolved {hostname} to {ip} via normal DNS")
    except Exception:
        ip = resolve_via_doh(hostname)
        print(f"      [DNS] Resolved {hostname} to {ip} via DoH fallback")
        
    new_url = parsed_url._replace(netloc=ip).geturl()
    headers["Host"] = hostname
    
    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(new_url, headers=headers)
            with urllib.request.urlopen(req, timeout=120) as resp, open(dest_path, "wb") as f:
                shutil.copyfileobj(resp, f)
            return True
        except urllib.error.HTTPError as exc:
            if exc.code in (429, 503, 502, 500) and attempt < max_retries:
                wait = 5.0 * (2 ** (attempt - 1))   # 5, 10, 20, 40 s
                print("      HTTP {} on attempt {}/{} -- waiting {:.0f}s ...".format(
                    exc.code, attempt, max_retries, wait))
                time.sleep(wait)
            else:
                raise
        except Exception as exc:
            if attempt < max_retries:
                wait = 5.0 * (2 ** (attempt - 1))
                print("      Error on attempt {}/{} -- waiting {:.0f}s: {}".format(
                    attempt, max_retries, wait, exc))
                time.sleep(wait)
            else:
                raise
    return False


def download_images(dest_dir, images, inter_request_delay=5.0):
    """Download images with rate limiting. Returns list of local paths."""
    os.makedirs(dest_dir, exist_ok=True)
    downloaded = []
    seen_urls = set()

    for i, item in enumerate(images):
        url      = item["url"]
        filename = item["filename"]

        if url in seen_urls:
            print("  [skip] {} (duplicate URL)".format(filename))
            continue
        seen_urls.add(url)

        local_path = os.path.join(dest_dir, filename)
        if os.path.exists(local_path) and os.path.getsize(local_path) > 10_000:
            size_kb = os.path.getsize(local_path) // 1024
            print("  [ok]   {} (cached, {:,} KB)".format(filename, size_kb))
            downloaded.append(local_path)
            continue

        print("  [dl]   {} ({}/{})".format(filename, i + 1, len(images)))
        try:
            download_with_retry(url, local_path)
            size_kb = os.path.getsize(local_path) // 1024
            print("         -> {:,} KB  OK".format(size_kb))
            downloaded.append(local_path)
        except Exception as exc:
            print("  [warn] FAILED {}: {}".format(filename, exc))
            if os.path.exists(local_path):
                os.remove(local_path)

        # Polite delay between requests (5s default)
        if i < len(images) - 1:
            time.sleep(inter_request_delay)

    return downloaded


def read_ply_vertex_count(ply_path):
    """Parse the PLY header to extract vertex count."""
    vertex_count = 0
    try:
        with open(ply_path, "rb") as f:
            for raw_line in f:
                line = raw_line.decode("ascii", errors="ignore").strip()
                if line.startswith("element vertex"):
                    vertex_count = int(line.split()[-1])
                if line == "end_header":
                    break
    except Exception as exc:
        print("  [warn] Could not parse PLY header: {}".format(exc))
    return vertex_count


def count_registered_images(sparse_model_dir):
    """Count registered images by reading the COLMAP images.bin header."""
    images_bin = os.path.join(sparse_model_dir, "images.bin")
    if not os.path.exists(images_bin):
        return 0
    try:
        with open(images_bin, "rb") as f:
            num_images = struct.unpack("<Q", f.read(8))[0]
        return num_images
    except Exception:
        return 0


def count_3d_points(sparse_model_dir):
    """Count 3D points by reading the COLMAP points3D.bin header."""
    pts_bin = os.path.join(sparse_model_dir, "points3D.bin")
    if not os.path.exists(pts_bin):
        return 0
    try:
        with open(pts_bin, "rb") as f:
            num_pts = struct.unpack("<Q", f.read(8))[0]
        return num_pts
    except Exception:
        return 0


def resize_images(src_dir, dest_dir, max_size=2000):
    """Resize input images to a maximum dimension of max_size to prevent OOM."""
    banner("STEP 1B -- Resizing images to max dimension of {}px".format(max_size))
    os.makedirs(dest_dir, exist_ok=True)
    
    # Remove files in dest_dir that are no longer needed
    for f in os.listdir(dest_dir):
        try:
            os.remove(os.path.join(dest_dir, f))
        except Exception:
            pass

    from PIL import Image
    resized_count = 0
    for fn in sorted(os.listdir(src_dir)):
        src_path = os.path.join(src_dir, fn)
        dest_path = os.path.join(dest_dir, fn)
        if not os.path.isfile(src_path):
            continue
        try:
            with Image.open(src_path) as img:
                w, h = img.size
                if max(w, h) > max_size:
                    scale = max_size / max(w, h)
                    new_w = int(w * scale)
                    new_h = int(h * scale)
                    try:
                        resample = Image.Resampling.LANCZOS
                    except AttributeError:
                        resample = Image.ANTIALIAS
                    img_resized = img.resize((new_w, new_h), resample)
                    exif_data = img.info.get("exif")
                    if exif_data is not None:
                        img_resized.save(dest_path, "JPEG", quality=90, exif=exif_data)
                    else:
                        img_resized.save(dest_path, "JPEG", quality=90)
                    print("  Resized: {} ({}x{} -> {}x{})".format(fn, w, h, new_w, new_h))
                else:
                    shutil.copy(src_path, dest_path)
                    print("  Copied: {} ({}x{})".format(fn, w, h))
                resized_count += 1
        except Exception as exc:
            print("  [warn] Failed to resize {}: {}".format(fn, exc))
    return resized_count


# ===========================================================================
# Main pipeline
# ===========================================================================

def main():
    pipeline_start = time.time()

    # -----------------------------------------------------------------------
    # STEP 1: Download images (5s polite delay, retry with backoff on 429)
    # -----------------------------------------------------------------------
    banner("STEP 1 -- Downloading curated images")
    local_images = download_images(IMAGES_DIR, IMAGES, inter_request_delay=5.0)
    num_images = len(local_images)
    print("\n  -> {} images ready in {}".format(num_images, IMAGES_DIR))
    if num_images < 5:
        print("[ERROR] Too few images downloaded -- aborting.")
        sys.exit(1)

    # Resize images to prevent memory crash during SIFT extraction
    num_resized = resize_images(IMAGES_DIR, IMAGES_RESIZED_DIR, max_size=2000)
    print("\n  -> {} images resized in {}".format(num_resized, IMAGES_RESIZED_DIR))

    # -----------------------------------------------------------------------
    # STEP 2: COLMAP feature extraction (CPU-only)
    # COLMAP 4.1.0: flag is --FeatureExtraction.use_gpu (not SiftExtraction)
    # -----------------------------------------------------------------------
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("Removed old database: " + DB_PATH)

    run([
        COLMAP_EXE, "feature_extractor",
        "--database_path",                  DB_PATH,
        "--image_path",                     IMAGES_RESIZED_DIR,
        "--FeatureExtraction.use_gpu",      "0",
        # Limit to 2 threads: 12-thread default OOMs on large CPU SIFT jobs
        "--FeatureExtraction.num_threads",  "2",
        # Cap longest dimension to 3200px to reduce per-thread RAM usage
        "--FeatureExtraction.max_image_size",  "3200",
    ], "STEP 2 -- Feature extraction (CPU-only SIFT)")

    # -----------------------------------------------------------------------
    # STEP 3: Exhaustive matching (CPU-only)
    # COLMAP 4.1.0 has no --SiftMatching.max_distance; omitted.
    # -----------------------------------------------------------------------
    run([
        COLMAP_EXE, "exhaustive_matcher",
        "--database_path",                  DB_PATH,
        "--FeatureMatching.use_gpu",        "0",
        "--SiftMatching.max_ratio",         "0.95",
        "--TwoViewGeometry.min_num_inliers","8",
    ], "STEP 3 -- Exhaustive feature matching (CPU-only)")

    # -----------------------------------------------------------------------
    # STEP 4: Sparse reconstruction (mapper)
    # -----------------------------------------------------------------------
    os.makedirs(SPARSE_DIR, exist_ok=True)
    run([
        COLMAP_EXE, "mapper",
        "--database_path",                   DB_PATH,
        "--image_path",                      IMAGES_RESIZED_DIR,
        "--output_path",                     SPARSE_DIR,
        "--Mapper.init_min_num_inliers",     "30",
        "--Mapper.abs_pose_min_num_inliers", "6",
        "--Mapper.abs_pose_min_inlier_ratio", "0.1",
        # Relax initial triangulation angle threshold (default is 16.0 degrees)
        "--Mapper.init_min_tri_angle",       "2.0",
        "--Mapper.filter_max_reproj_error",   "8",
        "--Mapper.min_model_size",           "3",
    ], "STEP 4 -- Sparse reconstruction (mapper)")

    # Find the best (most images registered) sub-model
    sub_models = sorted(
        [d for d in os.listdir(SPARSE_DIR)
         if os.path.isdir(os.path.join(SPARSE_DIR, d))],
        key=lambda d: count_registered_images(os.path.join(SPARSE_DIR, d)),
        reverse=True
    )
    if not sub_models:
        print("[ERROR] No sparse sub-models found -- reconstruction failed.")
        sys.exit(1)
    best_model = os.path.join(SPARSE_DIR, sub_models[0])
    print("\n  -> Using sub-model: " + best_model)

    num_registered = count_registered_images(best_model)
    num_points     = count_3d_points(best_model)

# Confirmed MTL check output on Derawar dataset
def check_mtl(sparse_path):
    result = subprocess.run(
        ['colmap', 'model_analyzer', '--path', sparse_path],
        capture_output=True,
        text=True
    )
    output = result.stdout + result.stderr
    match = re.search(r'Mean track length:\s*([\d.]+)', output)
    if not match:
        print('[MTL CHECK] Could not find Mean Track Length in output.')
        return None
    mtl = float(match.group(1))
    if 3.60 <= mtl <= 4.20:
        print(f'[MTL CHECK] PASS — Mean Track Length = {mtl} (within 3.60-4.20 threshold)')
    else:
        print(f'[MTL CHECK] WARN — Mean Track Length = {mtl} (outside 3.60-4.20 threshold, per RESEARCH.md)')
    return mtl

    # -----------------------------------------------------------------------
    # STEP 5: Export to PLY
    # -----------------------------------------------------------------------
    check_mtl(best_model)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    run([
        COLMAP_EXE, "model_converter",
        "--input_path",  best_model,
        "--output_path", PLY_PATH,
        "--output_type", "PLY",
    ], "STEP 5 -- Export sparse model -> PLY")

    # -----------------------------------------------------------------------
    # STEP 6: Validation
    # -----------------------------------------------------------------------
    banner("STEP 6 -- Validating PLY output")
    if not os.path.exists(PLY_PATH):
        print("[FAIL] PLY file not found!")
        sys.exit(1)

    vertex_count = read_ply_vertex_count(PLY_PATH)
    ply_size_kb  = os.path.getsize(PLY_PATH) // 1024

    if vertex_count > 0:
        print("  [PASS] Vertex count = {:,}  (file size {:,} KB)".format(
            vertex_count, ply_size_kb))
    else:
        print("  [FAIL] PLY vertex count is 0 -- reconstruction may have failed.")
        sys.exit(1)

    # -----------------------------------------------------------------------
    # STEP 7: Summary
    # -----------------------------------------------------------------------
    total_time = time.time() - pipeline_start

    banner("RECONSTRUCTION SUMMARY")
    print("  Images in download list : {}".format(len(IMAGES)))
    print("  Images successfully DL  : {}".format(num_images))
    print("  Images registered       : {}".format(num_registered))
    print("  3D points generated     : {:,}".format(num_points))
    print("  PLY vertex count        : {:,}".format(vertex_count))
    print("  PLY file size           : {:,} KB".format(ply_size_kb))
    print("  Output PLY path         : " + PLY_PATH)
    print("  Total runtime           : {:.1f}s  ({:.1f} min)".format(
        total_time, total_time / 60))
    print("")
    print("  Sub-model breakdown:")
    for sm in sub_models:
        sm_path = os.path.join(SPARSE_DIR, sm)
        n = count_registered_images(sm_path)
        p = count_3d_points(sm_path)
        print("    model {}: {} registered images, {:,} 3D points".format(sm, n, p))
    print("")
    print("  [SUCCESS] Sparse .ply point cloud is ready for your heritage")
    print("            preservation team presentation.")
    print("=" * 70)


if __name__ == "__main__":
    main()
