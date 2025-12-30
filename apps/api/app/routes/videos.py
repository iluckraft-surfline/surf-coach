from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from app.models.schemas import VideoUploadResponse
from app.services.worker import run_job_sync
import uuid
import os
from pathlib import Path

router = APIRouter()

# Get data directory path (relative to project root)
DATA_DIR = Path(__file__).parent.parent.parent.parent.parent / "data"
JOBS_DIR = DATA_DIR / "jobs"
JOBS_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/videos", response_model=VideoUploadResponse)
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """Upload a video file and create a job."""
    # Validate file format
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    ext = Path(file.filename).suffix.lower()
    if ext not in [".mp4", ".mov"]:
        raise HTTPException(
            status_code=400,
            detail="Unsupported format. Please upload MP4 or MOV."
        )
    
    # Validate file size (500MB limit)
    file_content = await file.read()
    file_size_mb = len(file_content) / (1024 * 1024)
    if file_size_mb > 500:
        raise HTTPException(
            status_code=400,
            detail="Video exceeds 500MB limit. Please compress or trim your video."
        )
    
    # Create job directory
    job_id = str(uuid.uuid4())
    job_dir = JOBS_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    
    # Save video file
    video_path = job_dir / "input.mp4"
    with open(video_path, "wb") as f:
        f.write(file_content)
    
    # Create initial job metadata
    import json
    job_meta = {
        "jobId": job_id,
        "status": "pending",
        "progress": 0,
        "createdAt": str(Path(video_path).stat().st_mtime)
    }
    meta_path = job_dir / "meta.json"
    with open(meta_path, "w") as f:
        json.dump(job_meta, f)
    
    # Start background processing
    background_tasks.add_task(run_job_sync, job_id)
    
    return VideoUploadResponse(jobId=job_id)

