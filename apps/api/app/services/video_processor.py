import cv2
import json
import subprocess
from pathlib import Path
from typing import Dict, Any
from app.config import JOBS_DIR, VIDEO_CODEC, VIDEO_FORMAT


def extract_video_metadata(video_path: Path) -> Dict[str, Any]:
    """Extract metadata from video file using OpenCV."""
    cap = cv2.VideoCapture(str(video_path))
    
    if not cap.isOpened():
        raise ValueError("Could not open video file")
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps if fps > 0 else 0
    
    cap.release()
    
    return {
        "fps": fps,
        "width": width,
        "height": height,
        "frameCount": frame_count,
        "duration": duration
    }


def normalize_video(input_path: Path, output_path: Path) -> None:
    """Transcode video to stable H.264 mp4 format using ffmpeg."""
    cmd = [
        "ffmpeg",
        "-i", str(input_path),
        "-c:v", VIDEO_CODEC,
        "-preset", "medium",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        "-movflags", "+faststart",
        "-y",  # Overwrite output file
        str(output_path)
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg transcoding failed: {e.stderr}")
    except FileNotFoundError:
        raise RuntimeError("FFmpeg not found. Please install ffmpeg.")


def save_metadata(job_dir: Path, metadata: Dict[str, Any]) -> None:
    """Save metadata to meta.json in job directory."""
    meta_path = job_dir / "meta.json"
    
    # Load existing metadata if it exists
    existing_meta = {}
    if meta_path.exists():
        with open(meta_path, "r") as f:
            existing_meta = json.load(f)
    
    # Update with new metadata
    existing_meta.update(metadata)
    
    # Save
    with open(meta_path, "w") as f:
        json.dump(existing_meta, f, indent=2)

