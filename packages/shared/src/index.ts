// Shared types between frontend and backend
export interface JobStatus {
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number
  error?: string
}

export interface Event {
  type: 'pop-up' | 'turn'
  timestamp: number
  confidence: number
}

export interface Tip {
  id: string
  message: string
  confidence: number
  timestamp?: number
  impact: 'high' | 'medium' | 'low'
}

export interface JobResults {
  metrics: {
    popUpTime?: number
    turnCount?: number
    averageSpeed?: number
    speedRetention?: number
    smoothness?: number
  }
  events: Event[]
  tips: Tip[]
}

export interface TrackFrame {
  frame: number
  bbox: number[]
  centroid: number[]
  trackId: number
}

export interface JobTracks {
  frames: TrackFrame[]
}

