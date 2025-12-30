from typing import List, Dict
import numpy as np
from app.config import (
    MIN_TIP_CONFIDENCE,
    DETECTION_QUALITY_WEIGHT,
    METRIC_RELIABILITY_WEIGHT
)


def calculate_confidence(
    tracks: List[Dict],
    speeds: List[float],
    headings: List[float]
) -> float:
    """
    Calculate overall confidence score for analysis.
    
    Combines detection quality and metric reliability.
    """
    if not tracks:
        return 0.0
    
    # Detection quality: average confidence × track continuity
    avg_detection_confidence = np.mean([t.get("confidence", 0.5) for t in tracks])
    track_continuity = 1.0 if len(tracks) > 10 else len(tracks) / 10.0
    detection_quality = avg_detection_confidence * track_continuity
    
    # Metric reliability: signal-to-noise ratio
    if speeds and len(speeds) > 1:
        speed_signal = np.mean(speeds)
        speed_noise = np.std(speeds)
        speed_snr = speed_signal / (speed_noise + 1e-6)
        speed_reliability = min(1.0, speed_snr / 10.0)  # Normalize
    else:
        speed_reliability = 0.0
    
    if headings and len(headings) > 1:
        heading_changes = np.diff(headings)
        heading_signal = np.mean(np.abs(heading_changes))
        heading_noise = np.std(heading_changes)
        heading_snr = heading_signal / (heading_noise + 1e-6)
        heading_reliability = min(1.0, heading_snr / 5.0)  # Normalize
    else:
        heading_reliability = 0.0
    
    metric_reliability = (speed_reliability + heading_reliability) / 2.0
    
    # Combined confidence
    combined_confidence = (
        detection_quality * DETECTION_QUALITY_WEIGHT +
        metric_reliability * METRIC_RELIABILITY_WEIGHT
    )
    
    return min(1.0, max(0.0, combined_confidence))


def generate_tips(
    metrics: Dict,
    events: List[Dict],
    overall_confidence: float
) -> List[Dict]:
    """
    Generate coaching tips based on metrics and events.
    
    Returns:
        List of tips with id, message, confidence, timestamp, impact
    """
    tips = []
    
    # Only generate tips if confidence is acceptable
    if overall_confidence < MIN_TIP_CONFIDENCE:
        return tips
    
    # Tip 1: Late pop-up
    if metrics.get("popUpTime") is not None and metrics["popUpTime"] > 2.0:
        tips.append({
            "id": "late-popup",
            "message": "Your pop-up is happening late. Try to pop up earlier to catch more of the wave.",
            "confidence": overall_confidence,
            "timestamp": metrics["popUpTime"],
            "impact": "medium"
        })
    
    # Tip 2: Speed loss in turns
    speed_retention = metrics.get("speedRetention", 1.0)
    if speed_retention < 0.8:  # Lost more than 20% speed
        # Find turn with worst speed retention
        worst_turn_timestamp = None
        if events:
            turn_events = [e for e in events if e["type"] == "turn"]
            if turn_events:
                worst_turn_timestamp = turn_events[0]["timestamp"]
        
        tips.append({
            "id": "speed-loss",
            "message": "You're losing speed in your turns. Try to maintain momentum by keeping your weight centered.",
            "confidence": overall_confidence,
            "timestamp": worst_turn_timestamp,
            "impact": "high"
        })
    
    # Tip 3: Too many turns
    turn_count = metrics.get("turnCount", 0)
    clip_duration = 30.0  # Default, should come from metadata
    turns_per_second = turn_count / clip_duration if clip_duration > 0 else 0
    if turns_per_second > 0.15:  # More than 0.15 turns per second
        tips.append({
            "id": "too-many-turns",
            "message": "You're making too many turns. Focus on fewer, more powerful turns.",
            "confidence": overall_confidence,
            "timestamp": None,
            "impact": "medium"
        })
    
    # Tip 4: Inconsistent speed
    if "averageSpeed" in metrics:
        # This would need speed variance - simplified for now
        smoothness = metrics.get("smoothness", 1.0)
        if smoothness < 0.6:
            tips.append({
                "id": "inconsistent-speed",
                "message": "Your speed is inconsistent. Try to maintain a steady pace throughout your ride.",
                "confidence": overall_confidence,
                "timestamp": None,
                "impact": "medium"
            })
    
    # Tip 5: Poor turn execution
    # This would need turn rate analysis - simplified for now
    
    # Rank tips by impact (high > medium > low)
    impact_order = {"high": 3, "medium": 2, "low": 1}
    tips.sort(key=lambda t: impact_order.get(t["impact"], 0), reverse=True)
    
    # Limit to top 3 tips
    return tips[:3]

