import { useRef, useEffect, useState, useCallback } from 'react'

interface TrackFrame {
  frame: number
  bbox: number[]
  centroid: number[]
  trackId: number
}

interface Event {
  type: string
  timestamp: number
  confidence: number
}

interface VideoPlayerWithCanvasOverlayProps {
  jobId: string
  tracks: TrackFrame[]
  events: Event[]
  onSeek?: (timestamp: number) => void
}

export function VideoPlayerWithCanvasOverlay({
  jobId,
  tracks,
  events,
  onSeek,
}: VideoPlayerWithCanvasOverlayProps) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [fps, setFps] = useState(30)

  const handleSeek = useCallback((timestamp: number) => {
    if (videoRef.current && onSeek) {
      videoRef.current.currentTime = timestamp
      onSeek(timestamp)
    }
  }, [onSeek])

  useEffect(() => {
    const video = videoRef.current
    const canvas = canvasRef.current
    if (!video || !canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const handleLoadedMetadata = () => {
      if (video && canvas) {
        canvas.width = video.videoWidth
        canvas.height = video.videoHeight
        // Estimate fps from video metadata if available
        // For now, use default 30
        setFps(30)
      }
    }

    const updateCanvas = () => {
      if (!video || !canvas || !ctx) return

      const currentTime = video.currentTime
      const currentFrame = Math.floor(currentTime * fps)

      // Clear canvas
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      // Find track data for current frame
      const trackData = tracks.find((t) => t.frame === currentFrame)
      if (trackData) {
        // Draw bounding box (green)
        ctx.strokeStyle = '#10b981'
        ctx.lineWidth = 2
        ctx.strokeRect(
          trackData.bbox[0],
          trackData.bbox[1],
          trackData.bbox[2] - trackData.bbox[0],
          trackData.bbox[3] - trackData.bbox[1]
        )

        // Draw trajectory (last 30 frames)
        const trajectoryFrames = tracks.filter(
          (t) => t.frame <= currentFrame && t.frame > currentFrame - 30
        )
        if (trajectoryFrames.length > 1) {
          ctx.strokeStyle = '#3b82f6'
          ctx.lineWidth = 2
          ctx.beginPath()
          ctx.moveTo(
            trajectoryFrames[0].centroid[0],
            trajectoryFrames[0].centroid[1]
          )
          for (let i = 1; i < trajectoryFrames.length; i++) {
            ctx.lineTo(
              trajectoryFrames[i].centroid[0],
              trajectoryFrames[i].centroid[1]
            )
          }
          ctx.stroke()
        }

        // Draw centroid
        ctx.fillStyle = '#3b82f6'
        ctx.beginPath()
        ctx.arc(
          trackData.centroid[0],
          trackData.centroid[1],
          4,
          0,
          2 * Math.PI
        )
        ctx.fill()
      }

      // Draw event markers
      events.forEach((event) => {
        const eventFrame = Math.floor(event.timestamp * fps)
        if (Math.abs(eventFrame - currentFrame) < 5) {
          // Show marker if within 5 frames
          const y = canvas.height * 0.1
          ctx.fillStyle = event.type === 'pop-up' ? '#ef4444' : '#eab308'
          ctx.beginPath()
          ctx.arc(canvas.width / 2, y, 8, 0, 2 * Math.PI)
          ctx.fill()
        }
      })
    }

    const handleTimeUpdate = () => {
      updateCanvas()
    }

    video.addEventListener('timeupdate', handleTimeUpdate)
    video.addEventListener('loadedmetadata', handleLoadedMetadata)

    // Initial setup
    if (video.readyState >= 1) {
      handleLoadedMetadata()
    }

    return () => {
      video.removeEventListener('timeupdate', handleTimeUpdate)
      video.removeEventListener('loadedmetadata', handleLoadedMetadata)
    }
  }, [tracks, events, fps])

  // Expose seek function to parent
  useEffect(() => {
    if (onSeek) {
      // Store seek handler for Timeline component
      (videoRef.current as any)?._seekHandler = handleSeek
    }
  }, [handleSeek, onSeek])

  return (
    <div className="relative">
      <video
        ref={videoRef}
        src={`/api/jobs/${jobId}/video`}
        controls
        className="w-full rounded-lg"
        onPlay={() => setIsPlaying(true)}
        onPause={() => setIsPlaying(false)}
      />
      <canvas
        ref={canvasRef}
        className="absolute top-0 left-0 w-full h-full pointer-events-none rounded-lg"
        style={{ imageRendering: 'pixelated' }}
      />
    </div>
  )
}

