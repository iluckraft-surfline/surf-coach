import json
import asyncio
from pathlib import Path
from typing import Dict

from app.services.video_processor import extract_video_metadata, save_metadata
from app.services.detection import process_video_detections
from app.services.tracking import SimpleTracker, smooth_tracks
from app.services.feature_extraction import (
    calculate_speed_proxy,
    calculate_heading,
    calculate_turn_rate,
    calculate_vertical_movement,
    smooth_signal
)
from app.services.event_detection import detect_popup, detect_turns
from app.services.metrics import calculate_metrics
from app.services.coaching import calculate_confidence, generate_tips
from app.config import JOBS_DIR


async def process_job(job_id: str) -> None:
    """
    Process a video job: detect, track, extract features, detect events, calculate metrics, generate tips.
    """
    job_dir = JOBS_DIR / job_id
    video_path = job_dir / "input.mp4"
    
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    # Update status to processing
    update_job_status(job_id, "processing", 0.1)
    
    # Step 1: Extract metadata
    metadata = extract_video_metadata(video_path)
    save_metadata(job_dir, metadata)
    update_job_status(job_id, "processing", 0.2)
    
    fps = metadata["fps"]
    frame_width = metadata["width"]
    frame_height = metadata["height"]
    
    # Step 2: Detection
    frame_detections = process_video_detections(video_path)
    update_job_status(job_id, "processing", 0.4)
    
    if not frame_detections or not any(d["detections"] for d in frame_detections):
        update_job_status(job_id, "failed", 0.0, "Could not detect a surfer in this video. Please ensure the surfer is clearly visible.")
        return
    
    # Step 3: Tracking
    tracker = SimpleTracker()
    all_tracked_frames = []
    
    for frame_data in frame_detections:
        frame_num = frame_data["frame"]
        detections = frame_data["detections"]
        
        tracked = tracker.update(detections)
        
        for track in tracked:
            all_tracked_frames.append({
                "frame": frame_num,
                **track
            })
    
    # Select primary surfer (largest track)
    primary_track_id = tracker.get_primary_track_id()
    if primary_track_id is None:
        update_job_status(job_id, "failed", 0.0, "Could not identify primary surfer track.")
        return
    
    # Filter to primary track only
    primary_tracks = [t for t in all_tracked_frames if t["trackId"] == primary_track_id]
    
    # Sort by frame number
    primary_tracks.sort(key=lambda x: x["frame"])
    
    # Smooth tracks
    primary_tracks = smooth_tracks(primary_tracks, window_size=5)
    
    update_job_status(job_id, "processing", 0.6)
    
    # Step 4: Feature extraction
    speeds = calculate_speed_proxy(primary_tracks, fps, frame_width, frame_height)
    headings = calculate_heading(primary_tracks)
    turn_rates = calculate_turn_rate(headings, fps)
    vertical_velocities = calculate_vertical_movement(primary_tracks)
    
    # Smooth signals
    speeds = smooth_signal(speeds)
    turn_rates = smooth_signal(turn_rates)
    
    update_job_status(job_id, "processing", 0.7)
    
    # Step 5: Event detection
    popup_events = detect_popup(primary_tracks, vertical_velocities, fps)
    turn_events = detect_turns(turn_rates, fps)
    all_events = popup_events + turn_events
    
    update_job_status(job_id, "processing", 0.8)
    
    # Step 6: Metrics calculation
    metrics = calculate_metrics(primary_tracks, speeds, turn_rates, all_events, fps)
    
    # Step 7: Coaching tips
    overall_confidence = calculate_confidence(primary_tracks, speeds, headings)
    tips = generate_tips(metrics, all_events, overall_confidence)
    
    update_job_status(job_id, "processing", 0.9)
    
    # Step 8: Save results
    results = {
        "metrics": metrics,
        "events": all_events,
        "tips": tips
    }
    
    results_path = job_dir / "results.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    
    # Save tracks
    tracks_data = {
        "frames": [
            {
                "frame": t["frame"],
                "bbox": t["bbox"],
                "centroid": t["centroid"],
                "trackId": t["trackId"]
            }
            for t in primary_tracks
        ]
    }
    
    tracks_path = job_dir / "tracks.json"
    with open(tracks_path, "w") as f:
        json.dump(tracks_data, f, indent=2)
    
    # Update status to completed
    update_job_status(job_id, "completed", 1.0)


def run_job_sync(job_id: str) -> None:
    """Run job processing synchronously in background thread."""
    asyncio.run(process_job(job_id))


def update_job_status(job_id: str, status: str, progress: float, error: str = None) -> None:
    """Update job status in meta.json."""
    job_dir = JOBS_DIR / job_id
    meta_path = job_dir / "meta.json"
    
    # Load existing metadata
    meta = {}
    if meta_path.exists():
        with open(meta_path, "r") as f:
            meta = json.load(f)
    
    # Update status
    meta["status"] = status
    meta["progress"] = progress
    if error:
        meta["error"] = error
    
    # Save
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)



