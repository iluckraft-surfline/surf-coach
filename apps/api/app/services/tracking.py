from typing import List, Dict, Tuple
import numpy as np
from collections import defaultdict


class SimpleTracker:
    """Simple tracking implementation using IoU matching."""
    
    def __init__(self, iou_threshold: float = 0.3):
        self.iou_threshold = iou_threshold
        self.tracks = {}  # track_id -> list of detections
        self.next_track_id = 1
        self.max_missing_frames = 5
    
    def calculate_iou(self, bbox1: List[float], bbox2: List[float]) -> float:
        """Calculate Intersection over Union (IoU) between two bounding boxes."""
        x1_1, y1_1, x2_1, y2_1 = bbox1
        x1_2, y1_2, x2_2, y2_2 = bbox2
        
        # Calculate intersection
        x1_i = max(x1_1, x1_2)
        y1_i = max(y1_1, y1_2)
        x2_i = min(x2_1, x2_2)
        y2_i = min(y2_1, y2_2)
        
        if x2_i < x1_i or y2_i < y1_i:
            return 0.0
        
        intersection = (x2_i - x1_i) * (y2_i - y1_i)
        area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
        area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
        union = area1 + area2 - intersection
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    def get_centroid(self, bbox: List[float]) -> Tuple[float, float]:
        """Calculate centroid of bounding box."""
        x1, y1, x2, y2 = bbox
        return ((x1 + x2) / 2, (y1 + y2) / 2)
    
    def update(self, frame_detections: List[Dict]) -> List[Dict]:
        """
        Update tracker with new detections.
        
        Args:
            frame_detections: List of detections with 'bbox' and 'confidence'
        
        Returns:
            List of tracked detections with 'trackId', 'bbox', 'centroid'
        """
        if not frame_detections:
            return []
        
        # Match detections to existing tracks
        matched_tracks = set()
        tracked_detections = []
        
        for det in frame_detections:
            best_iou = 0
            best_track_id = None
            
            # Find best matching track
            for track_id, track_history in self.tracks.items():
                if not track_history:
                    continue
                
                # Get last detection in track
                last_det = track_history[-1]
                iou = self.calculate_iou(det["bbox"], last_det["bbox"])
                
                if iou > best_iou and iou > self.iou_threshold:
                    best_iou = iou
                    best_track_id = track_id
            
            # Assign to best track or create new track
            if best_track_id is not None:
                track_id = best_track_id
                matched_tracks.add(track_id)
            else:
                track_id = self.next_track_id
                self.next_track_id += 1
                self.tracks[track_id] = []
            
            # Add to track
            centroid = self.get_centroid(det["bbox"])
            tracked_det = {
                "trackId": track_id,
                "bbox": det["bbox"],
                "centroid": list(centroid),
                "confidence": det["confidence"]
            }
            self.tracks[track_id].append(tracked_det)
            tracked_detections.append(tracked_det)
        
        # Remove tracks that haven't been matched for too long
        tracks_to_remove = []
        for track_id in self.tracks:
            if track_id not in matched_tracks:
                # This is a simple implementation - in production, track missing frames
                pass
        
        return tracked_detections
    
    def get_primary_track_id(self) -> int:
        """Get track ID with largest average bounding box area."""
        if not self.tracks:
            return None
        
        track_areas = {}
        for track_id, track_history in self.tracks.items():
            if not track_history:
                continue
            
            areas = []
            for det in track_history:
                x1, y1, x2, y2 = det["bbox"]
                area = (x2 - x1) * (y2 - y1)
                areas.append(area)
            
            track_areas[track_id] = np.mean(areas)
        
        if not track_areas:
            return None
        
        return max(track_areas.items(), key=lambda x: x[1])[0]


def smooth_tracks(tracks: List[Dict], window_size: int = 5) -> List[Dict]:
    """Smooth bounding boxes and centroids using moving average."""
    if len(tracks) < window_size:
        return tracks
    
    smoothed = []
    for i in range(len(tracks)):
        start_idx = max(0, i - window_size // 2)
        end_idx = min(len(tracks), i + window_size // 2 + 1)
        window = tracks[start_idx:end_idx]
        
        # Average bbox
        avg_bbox = [
            np.mean([t["bbox"][j] for t in window]) for j in range(4)
        ]
        
        # Average centroid
        avg_centroid = [
            np.mean([t["centroid"][j] for t in window]) for j in range(2)
        ]
        
        smoothed_track = tracks[i].copy()
        smoothed_track["bbox"] = avg_bbox
        smoothed_track["centroid"] = avg_centroid
        smoothed.append(smoothed_track)
    
    return smoothed

