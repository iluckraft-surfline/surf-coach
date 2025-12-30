# Surf Coaching App – Local Web MVP Implementation Plan

## 0) MVP Definition

### User Flow

1. Open web app
2. Upload surf clip (mp4/mov)
3. See upload + analysis progress
4. View results:

   * Detected events (pop-up, turns)
   * Metrics (speed proxy, turn count, speed retention)
   * Coaching tips with timestamps
5. Watch video with overlays (bbox, trajectory, event markers)

### Constraints

* Runs locally
* No auth, no cloud
* Reasonable runtime (30–120s per clip)
* Only show tips when confidence is acceptable

---

## 1) Architecture Overview

### Processes

* **Frontend**: Vite + React + TanStack Router + TanStack Query
* **Backend API**: Python FastAPI
* **Worker**: Local Python inference pipeline
* **Storage**: Local filesystem

### Data Flow

1. Frontend uploads video
2. Backend creates job + saves file
3. Worker processes video
4. Outputs JSON artifacts + optional overlay
5. Frontend polls and renders results

---

## 2) Repository Structure

```
surf-coach/
  apps/
    web/
    api/
  packages/
    shared/
  data/
    uploads/
    jobs/
      <job_id>/
        input.mp4
        meta.json
        tracks.json
        results.json
        overlay.mp4 (optional)
```

---

## 3) Core Technology Choices

* **Video**: ffmpeg
* **Detection**: YOLOv8 (Ultralytics)
* **Tracking**: ByteTrack (or simple NN tracking initially)
* **Pose (v2)**: MediaPipe Pose
* **Backend**: FastAPI
* **Frontend**: TanStack Router + Query

---

## 4) Backend API Design

### Endpoints

* `POST /api/videos` → upload + create job
* `GET /api/jobs/{jobId}` → status + progress
* `GET /api/jobs/{jobId}/results`
* `GET /api/jobs/{jobId}/tracks`
* `GET /api/jobs/{jobId}/video`
* `GET /api/jobs/{jobId}/overlay` (optional)

### Job State

Stored as `job.json` in job directory.

---

## 5) Inference Pipeline

### A) Ingest & Normalize

* Save upload
* Transcode to stable format
* Extract metadata

### B) Detection

* Run YOLO per frame (or every N frames)
* Filter person class

### C) Tracking

* Associate detections across frames
* Choose primary surfer
* Smooth bbox + centroid

### D) Feature Extraction

* Speed proxy (px/sec normalized)
* Heading + turn rate
* Vertical movement proxy

### E) Event Detection

* Pop-up detection (bbox height & motion change)
* Turn detection (heading rate peaks)

### F) Metrics

* Pop-up time
* Turn count
* Avg speed
* Speed retention in turns
* Smoothness proxy

### G) Coaching Rules

* Rule-based mapping from metrics → tips
* Rank by confidence + impact
* Limit to top 1–3 tips

---

## 6) Frontend Plan (TanStack)

### Routes

* `/` Upload
* `/jobs/:jobId` Processing
* `/jobs/:jobId/results` Results

### Key Components

* UploadCard
* JobProgress
* VideoPlayerWithCanvasOverlay
* Timeline (events)
* MetricsPanel
* TipsPanel

### Overlay Strategy

* `<video>` + `<canvas>` overlay
* Sync using `currentTime`
* Draw bbox, trajectory, event markers

---

## 7) Implementation Roadmap

### Phase 1 – Skeleton

* Repo setup
* Fake jobs + dummy results
* End-to-end UX

### Phase 2 – Video Plumbing

* ffmpeg normalize
* Serve video
* Canvas overlay working

### Phase 3 – Detection & Tracking

* YOLO integration
* Tracking
* Real bbox overlays

### Phase 4 – Metrics & Events

* Speed/heading extraction
* Turn & pop-up heuristics

### Phase 5 – Coaching Rules

* Rule engine
* Confidence gating

### Phase 6 – Polish

* Multi-surfer selection
* Clip trimming
* Performance tuning

---

## 8) Performance Considerations

* Process every 2–3 frames
* Interpolate between frames
* Cache by video hash

---

## 9) Testing

* Unit tests for signal processing
* Golden-file tests for results.json
* Basic frontend e2e tests

---

## 10) MVP Success Criteria

* Stable tracking across clip
* Turn markers land near real turns
* At least one tip feels useful to surfers
