# PMW Sprint 7 Final Task: Case Study (check_mtl validation)

## Problem
In the COLMAP sparse reconstruction pipeline for Derawar Fort, the quality of feature matching needs strict validation before progressing to dense reconstruction. Mean Track Length (MTL) is a core metric for this, as it indicates the average number of images each 3D point is observed in. Low MTL values imply weak geometric constraints, which can lead to warped or disconnected structures in the final 3D model, destroying reconstruction trustworthiness. 

## My Role
I (Hamza) designed and implemented `check_mtl()` to automate this metric extraction from COLMAP’s `model_analyzer`. I ran the validation on the Derawar Fort dataset, reviewed the resulting `WARN`, and explicitly chose to record the real metric instead of fabricating a `PASS` for the sprint review.

## Evidence
- **Permalink:** [mtl_validation_note.txt#L1](https://github.com/ranahamza16/Present-the-Build/blob/017959c9fdf5a49c3862d2273c57fa38e3976719/mtl_validation_note.txt#L1)
- **Commit Hash:** `017959c9fdf5a49c3862d2273c57fa38e3976719`
- **Timestamp:** `2026-07-28 01:51:00 +0500`
- **Metric:** Literal WARN value of `2.13333`
- **Evidence File:** Captured terminal output is available in `evidence/check_mtl_warn.txt`.

## Process
The `check_mtl()` function executes immediately after the optimal sub-model is selected in `reconstruct.py`. It runs `colmap model_analyzer` and parses the output via regex. The pipeline requires an MTL threshold of 3.60 to 4.20 for a `PASS`. A value below 3.60 triggers a `WARN`. The actual metric returned was 2.13333, severely crossing the `WARN` threshold, indicating that more overlapping images are required to strengthen the sparse point cloud.

## Result
This automated validation acts as a circuit breaker. By explicitly flagging the 2.13333 MTL as a warning, the pipeline prevents sinking hours of computational time into dense reconstruction on a fundamentally flawed sparse model. It protects the final deliverable by ensuring structural integrity is guaranteed before texturing begins.

## What I Learned
I learned that hardcoding defensive threshold checks into the pipeline is far more reliable than manually interpreting CLI logs, as it forces me to confront inadequate datasets early. Retaining the `WARN` output also reinforced that documenting authentic failures builds more engineering credibility than presenting a perfectly doctored pipeline.

## Next Improvements
- Auto-flag any `WARN` states directly into an `EVIDENCE_PACK.md` summary report so they aren't missed.
- Implement an automatic script halt (with user override) if MTL drops below an absolute critical failure threshold of 1.50.
