from ultralytics import YOLO
import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple
from app.config import YOLO_MODEL, FRAME_PROCESSING_INTERVAL

# Global model instance (lazy loaded)
_model = None


def get_model():
    """Get or load YOLO model (singleton)."""
    global _model
    if _model is None:
        _model = YOLO(YOLO_MODEL)
    return _model


def detect_persons_in_frame(frame: np.ndarray) -> List[Tuple[float, float, float, float, float]]:
    """
    Detect persons in a frame using YOLOv8.
    
    Returns list of detections: [(x1, y1, x2, y2, confidence), ...]
    """
    model = get_model()
    results = model(frame, verbose=False)
    
    detections = []
    for result in results:
        boxes = result.boxes
        for box in boxes:
            # Filter for person class (class 0)
            if int(box.cls) == 0:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                confidence = float(box.conf[0].cpu().numpy())
                detections.append((x1, y1, x2, y2, confidence))
    
    return detections


def process_video_detections(video_path: Path) -> List[dict]:
    """
    Process video and detect persons in frames.
    
    Returns list of detections per frame: [{frame: int, detections: [...]}, ...]
    """
    cap = cv2.VideoCapture(str(video_path))
    
    if not cap.isOpened():
        raise ValueError("Could not open video file")
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = FRAME_PROCESSING_INTERVAL
    
    all_detections = []
    frame_number = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Process every Nth frame
        if frame_number % frame_interval == 0:
            detections = detect_persons_in_frame(frame)
            all_detections.append({
                "frame": frame_number,
                "detections": [
                    {
                        "bbox": [float(x1), float(y1), float(x2), float(y2)],
                        "confidence": float(conf)
                    }
                    for x1, y1, x2, y2, conf in detections
                ]
            })
        
        frame_number += 1
    
    cap.release()
    return all_detections

