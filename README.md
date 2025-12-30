# Surf Coach

A local web application that analyzes surf video footage and provides personalized coaching tips to help surfers improve their technique.

## Features

- **Video Upload**: Upload MP4 or MOV files up to 500MB
- **Person Detection**: Uses YOLOv8 to detect surfers in video frames
- **Tracking**: Tracks the primary surfer across frames using IoU-based tracking
- **Event Detection**: Automatically detects pop-ups and turns
- **Metrics Calculation**: Calculates speed, turn count, speed retention, and smoothness
- **Coaching Tips**: Provides personalized tips based on detected patterns

## Architecture

- **Frontend**: React + Vite + TanStack Router + TanStack Query
- **Backend**: FastAPI (Python)
- **Detection**: YOLOv8 (Ultralytics)
- **Video Processing**: OpenCV + ffmpeg

## Setup

### Prerequisites

- Node.js 18+ and pnpm
- Python 3.10+
- ffmpeg (for video processing)

Install ffmpeg:
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

### Installation

1. Install dependencies:
```bash
# Install pnpm if you don't have it
npm install -g pnpm

# Install frontend dependencies
pnpm install

# Install backend dependencies
cd apps/api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Start the backend:
```bash
cd apps/api
source venv/bin/activate  # On Windows: venv\Scripts\activate
pnpm dev
# Or: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

3. Start the frontend (in a new terminal):
```bash
pnpm dev:web
```

4. Open http://localhost:5173 in your browser

## Usage

1. Upload a video of yourself surfing (MP4 or MOV format)
2. Wait for processing (typically 30-120 seconds)
3. View results:
   - Watch video with bounding box and trajectory overlays
   - See detected events (pop-ups, turns) on the timeline
   - Review calculated metrics
   - Read personalized coaching tips

## Project Structure

```
surf-coach/
├── apps/
│   ├── web/          # React frontend
│   └── api/           # FastAPI backend
├── packages/
│   └── shared/        # Shared TypeScript types
└── data/
    ├── uploads/       # Uploaded videos
    └── jobs/          # Processing jobs and results
```

## Development

The app processes videos locally - no cloud services required. All data stays on your machine.

## License

MIT
