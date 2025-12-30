from typing import List, Dict
import numpy as np
from app.config import (
    POPUP_HEIGHT_INCREASE_THRESHOLD,
    POPUP_TIME_WINDOW,
    POPUP_VERTICAL_VELOCITY_THRESHOLD,
    TURN_ANGULAR_VELOCITY_THRESHOLD,
    TURN_MIN_DURATION
)


def detect_popup(
    tracks: List[Dict],
    vertical_velocities: List[float],
    fps: float
) -> List[Dict]:
    """
    Detect pop-up events based on bbox height increase and vertical motion.
    
    Returns:
        List of pop-up events: [{timestamp: float, confidence: float}, ...]
    """
    events = []
    
    if len(tracks) < 2:
        return events
    
    window_frames = int(POPUP_TIME_WINDOW * fps)
    
    for i in range(window_frames, len(tracks)):
        # Get bbox heights
        current_bbox = tracks[i]["bbox"]
        past_bbox = tracks[i - window_frames]["bbox"]
        
        current_height = current_bbox[3] - current_bbox[1]
        past_height = past_bbox[3] - past_bbox[1]
        
        # Check height increase
        height_increase = (current_height - past_height) / past_height if past_height > 0 else 0
        
        # Check vertical velocity spike
        recent_velocities = vertical_velocities[max(0, i - window_frames):i]
        max_velocity = max(recent_velocities) if recent_velocities else 0
        
        # Detect pop-up
        if height_increase > POPUP_HEIGHT_INCREASE_THRESHOLD and abs(max_velocity) > POPUP_VERTICAL_VELOCITY_THRESHOLD:
            timestamp = i / fps
            # Confidence based on how strong the signal is
            confidence = min(1.0, (height_increase / POPUP_HEIGHT_INCREASE_THRESHOLD) * 0.5 + 0.5)
            
            events.append({
                "type": "pop-up",
                "timestamp": timestamp,
                "confidence": confidence
            })
    
    return events


def detect_turns(
    turn_rates: List[float],
    fps: float
) -> List[Dict]:
    """
    Detect turn events based on heading rate peaks.
    
    Returns:
        List of turn events: [{timestamp: float, confidence: float}, ...]
    """
    events = []
    
    if len(turn_rates) < 2:
        return events
    
    # Smooth turn rates first
    smoothed_rates = []
    window_size = 5
    for i in range(len(turn_rates)):
        start_idx = max(0, i - window_size // 2)
        end_idx = min(len(turn_rates), i + window_size // 2 + 1)
        smoothed_rates.append(np.mean(turn_rates[start_idx:end_idx]))
    
    min_duration_frames = int(TURN_MIN_DURATION * fps)
    in_turn = False
    turn_start_frame = 0
    
    for i in range(1, len(smoothed_rates)):
        abs_rate = abs(smoothed_rates[i])
        
        if abs_rate > TURN_ANGULAR_VELOCITY_THRESHOLD:
            if not in_turn:
                in_turn = True
                turn_start_frame = i
        else:
            if in_turn:
                # End of turn
                turn_duration = (i - turn_start_frame) / fps
                if turn_duration >= TURN_MIN_DURATION:
                    # Use middle of turn as timestamp
                    turn_mid_frame = (turn_start_frame + i) // 2
                    timestamp = turn_mid_frame / fps
                    
                    # Calculate confidence based on peak turn rate
                    peak_rate = max([abs(smoothed_rates[j]) for j in range(turn_start_frame, i)])
                    confidence = min(1.0, peak_rate / (TURN_ANGULAR_VELOCITY_THRESHOLD * 2))
                    
                    events.append({
                        "type": "turn",
                        "timestamp": timestamp,
                        "confidence": confidence
                    })
                in_turn = False
    
    # Handle turn that extends to end of video
    if in_turn:
        turn_duration = (len(smoothed_rates) - turn_start_frame) / fps
        if turn_duration >= TURN_MIN_DURATION:
            turn_mid_frame = (turn_start_frame + len(smoothed_rates)) // 2
            timestamp = turn_mid_frame / fps
            peak_rate = max([abs(smoothed_rates[j]) for j in range(turn_start_frame, len(smoothed_rates))])
            confidence = min(1.0, peak_rate / (TURN_ANGULAR_VELOCITY_THRESHOLD * 2))
            
            events.append({
                "type": "turn",
                "timestamp": timestamp,
                "confidence": confidence
            })
    
    return events

