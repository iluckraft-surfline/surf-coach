from typing import List, Dict
import numpy as np


def calculate_metrics(
    tracks: List[Dict],
    speeds: List[float],
    turn_rates: List[float],
    events: List[Dict],
    fps: float
) -> Dict:
    """
    Calculate all metrics from tracks and events.
    
    Returns:
        Dictionary with metrics
    """
    metrics = {}
    
    # Pop-up time (first pop-up event)
    popup_events = [e for e in events if e["type"] == "pop-up"]
    if popup_events:
        metrics["popUpTime"] = popup_events[0]["timestamp"]
    else:
        metrics["popUpTime"] = None
    
    # Turn count
    turn_events = [e for e in events if e["type"] == "turn"]
    metrics["turnCount"] = len(turn_events)
    
    # Average speed
    if speeds:
        metrics["averageSpeed"] = np.mean(speeds)
    else:
        metrics["averageSpeed"] = 0.0
    
    # Speed retention in turns
    if turn_events and speeds:
        speed_retentions = []
        for turn_event in turn_events:
            turn_frame = int(turn_event["timestamp"] * fps)
            if turn_frame < len(speeds):
                # Speed before turn (average of 10 frames before)
                before_start = max(0, turn_frame - 10)
                before_speed = np.mean(speeds[before_start:turn_frame]) if turn_frame > 0 else speeds[turn_frame]
                
                # Speed during turn (average of 10 frames during)
                during_end = min(len(speeds), turn_frame + 10)
                during_speed = np.mean(speeds[turn_frame:during_end])
                
                if before_speed > 0:
                    retention = during_speed / before_speed
                    speed_retentions.append(retention)
        
        if speed_retentions:
            metrics["speedRetention"] = np.mean(speed_retentions)
        else:
            metrics["speedRetention"] = 1.0
    else:
        metrics["speedRetention"] = 1.0
    
    # Smoothness proxy (inverse of variance in turn rate)
    if turn_rates:
        turn_rate_variance = np.var(turn_rates)
        # Normalize to 0-1 scale (assuming max variance of 10000)
        smoothness = 1.0 / (1.0 + turn_rate_variance / 10000.0)
        metrics["smoothness"] = smoothness
    else:
        metrics["smoothness"] = 0.0
    
    return metrics

