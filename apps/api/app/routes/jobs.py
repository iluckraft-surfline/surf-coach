from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.models.schemas import JobStatus, JobResults, JobTracks
from pathlib import Path
import json

router = APIRouter()

# Get data directory path
DATA_DIR = Path(__file__).parent.parent.parent.parent.parent / "data"
JOBS_DIR = DATA_DIR / "jobs"


@router.get("/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Get job status and progress."""
    job_dir = JOBS_DIR / job_id
    
    if not job_dir.exists():
        raise HTTPException(status_code=404, detail="Job not found")
    
    meta_path = job_dir / "meta.json"
    if not meta_path.exists():
        raise HTTPException(status_code=404, detail="Job metadata not found")
    
    with open(meta_path, "r") as f:
        meta = json.load(f)
    
    return JobStatus(
        status=meta.get("status", "pending"),
        progress=meta.get("progress", 0),
        error=meta.get("error")
    )


@router.get("/{job_id}/results", response_model=JobResults)
async def get_job_results(job_id: str):
    """Get analysis results for a job."""
    job_dir = JOBS_DIR / job_id
    
    if not job_dir.exists():
        raise HTTPException(status_code=404, detail="Job not found")
    
    results_path = job_dir / "results.json"
    if not results_path.exists():
        raise HTTPException(status_code=404, detail="Results not yet available. Job may still be processing.")
    
    with open(results_path, "r") as f:
        results = json.load(f)
    
    return JobResults(**results)


@router.get("/{job_id}/tracks", response_model=JobTracks)
async def get_job_tracks(job_id: str):
    """Get tracking data for a job."""
    job_dir = JOBS_DIR / job_id
    
    if not job_dir.exists():
        raise HTTPException(status_code=404, detail="Job not found")
    
    tracks_path = job_dir / "tracks.json"
    if not tracks_path.exists():
        raise HTTPException(status_code=404, detail="Tracks not yet available. Job may still be processing.")
    
    with open(tracks_path, "r") as f:
        tracks = json.load(f)
    
    return JobTracks(**tracks)


@router.get("/{job_id}/video")
async def get_job_video(job_id: str):
    """Stream the processed video file."""
    job_dir = JOBS_DIR / job_id
    
    if not job_dir.exists():
        raise HTTPException(status_code=404, detail="Job not found")
    
    video_path = job_dir / "input.mp4"
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video not found")
    
    return FileResponse(
        video_path,
        media_type="video/mp4",
        headers={"Accept-Ranges": "bytes"}
    )


@router.get("/{job_id}/overlay")
async def get_job_overlay(job_id: str):
    """Stream overlay video if available."""
    job_dir = JOBS_DIR / job_id
    
    if not job_dir.exists():
        raise HTTPException(status_code=404, detail="Job not found")
    
    overlay_path = job_dir / "overlay.mp4"
    if not overlay_path.exists():
        raise HTTPException(status_code=404, detail="Overlay not found")
    
    return FileResponse(
        overlay_path,
        media_type="video/mp4",
        headers={"Accept-Ranges": "bytes"}
    )

