from typing import List, Dict
import numpy as np


def calculate_speed_proxy(tracks: List[Dict], fps: float, frame_width: int, frame_height: int) -> List[float]:
    """
    Calculate speed proxy (px/sec normalized by frame dimensions).
    
    Args:
        tracks: List of track frames with 'centroid'
        fps: Frames per second
        frame_width: Video frame width
        frame_height: Video frame height
    
    Returns:
        List of speed values (normalized px/sec)
    """
    speeds = [0.0]  # First frame has no speed
    
    for i in range(1, len(tracks)):
        prev_centroid = tracks[i-1]["centroid"]
        curr_centroid = tracks[i]["centroid"]
        
        # Calculate pixel distance
        dx = curr_centroid[0] - prev_centroid[0]
        dy = curr_centroid[1] - prev_centroid[1]
        distance_px = np.sqrt(dx**2 + dy**2)
        
        # Convert to px/sec
        speed_px_per_sec = distance_px * fps
        
        # Normalize by frame diagonal
        frame_diagonal = np.sqrt(frame_width**2 + frame_height**2)
        normalized_speed = speed_px_per_sec / frame_diagonal
        
        speeds.append(normalized_speed)
    
    return speeds


def calculate_heading(tracks: List[Dict]) -> List[float]:
    """
    Calculate heading (direction) from centroid trajectory.
    
    Returns:
        List of heading angles in radians
    """
    headings = [0.0]  # First frame has no heading
    
    for i in range(1, len(tracks)):
        prev_centroid = tracks[i-1]["centroid"]
        curr_centroid = tracks[i]["centroid"]
        
        dx = curr_centroid[0] - prev_centroid[0]
        dy = curr_centroid[1] - prev_centroid[1]
        
        # Calculate angle in radians
        heading = np.arctan2(dy, dx)
        headings.append(heading)
    
    return headings


def calculate_turn_rate(headings: List[float], fps: float) -> List[float]:
    """
    Calculate angular velocity (turn rate) from heading changes.
    
    Returns:
        List of turn rates in degrees per second
    """
    turn_rates = [0.0]
    
    for i in range(1, len(headings)):
        # Calculate angular change
        delta_heading = headings[i] - headings[i-1]
        
        # Normalize to [-pi, pi]
        delta_heading = np.arctan2(np.sin(delta_heading), np.cos(delta_heading))
        
        # Convert to degrees per second
        turn_rate_deg_per_sec = np.degrees(delta_heading) * fps
        turn_rates.append(turn_rate_deg_per_sec)
    
    return turn_rates


def calculate_vertical_movement(tracks: List[Dict]) -> List[float]:
    """
    Calculate vertical movement proxy from bbox bottom y-coordinate changes.
    
    Returns:
        List of vertical velocities (positive = moving down, negative = moving up)
    """
    vertical_velocities = [0.0]
    
    for i in range(1, len(tracks)):
        prev_bbox = tracks[i-1]["bbox"]
        curr_bbox = tracks[i]["bbox"]
        
        # Bottom y-coordinate (higher y = lower on screen)
        prev_bottom_y = prev_bbox[3]
        curr_bottom_y = curr_bbox[3]
        
        # Change in y (positive = moving down)
        delta_y = curr_bottom_y - prev_bottom_y
        vertical_velocities.append(delta_y)
    
    return vertical_velocities


def smooth_signal(signal: List[float], window_size: int = 5) -> List[float]:
    """Smooth signal using moving average."""
    if len(signal) < window_size:
        return signal
    
    smoothed = []
    for i in range(len(signal)):
        start_idx = max(0, i - window_size // 2)
        end_idx = min(len(signal), i + window_size // 2 + 1)
        window = signal[start_idx:end_idx]
        smoothed.append(np.mean(window))
    
    return smoothed

