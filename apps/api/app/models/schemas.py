from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class VideoUploadResponse(BaseModel):
    jobId: str


class JobStatus(BaseModel):
    status: str  # 'pending' | 'processing' | 'completed' | 'failed'
    progress: float  # 0.0 to 1.0
    error: Optional[str] = None


class Event(BaseModel):
    type: str  # 'pop-up' | 'turn'
    timestamp: float
    confidence: float


class Tip(BaseModel):
    id: str
    message: str
    confidence: float
    timestamp: Optional[float] = None
    impact: str  # 'high' | 'medium' | 'low'


class JobResults(BaseModel):
    metrics: Dict[str, Any]
    events: List[Event]
    tips: List[Tip]


class TrackFrame(BaseModel):
    frame: int
    bbox: List[float]  # [x1, y1, x2, y2]
    centroid: List[float]  # [x, y]
    trackId: int


class JobTracks(BaseModel):
    frames: List[TrackFrame]

