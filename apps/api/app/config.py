from pathlib import Path

# Detection model settings
YOLO_MODEL = "yolov8n.pt"  # or yolov8s.pt for better accuracy
FRAME_PROCESSING_INTERVAL = 3  # Process every 3 frames

# Event detection thresholds
POPUP_HEIGHT_INCREASE_THRESHOLD = 0.3  # 30% increase
POPUP_TIME_WINDOW = 0.5  # seconds
POPUP_VERTICAL_VELOCITY_THRESHOLD = 10  # pixels per frame

TURN_ANGULAR_VELOCITY_THRESHOLD = 45  # degrees per second
TURN_MIN_DURATION = 0.3  # seconds

# Confidence thresholds
MIN_TIP_CONFIDENCE = 0.7
DETECTION_QUALITY_WEIGHT = 0.7
METRIC_RELIABILITY_WEIGHT = 0.3

# File limits
MAX_FILE_SIZE_MB = 500

# Video processing
VIDEO_CODEC = "libx264"
VIDEO_FORMAT = "mp4"

# Data directories (relative to project root)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
JOBS_DIR = DATA_DIR / "jobs"
UPLOADS_DIR = DATA_DIR / "uploads"

