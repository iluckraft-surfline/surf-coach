import { createFileRoute } from '@tanstack/react-router'
import { VideoPlayerWithCanvasOverlay } from '@/components/VideoPlayerWithCanvasOverlay'
import { Timeline } from '@/components/Timeline'
import { MetricsPanel } from '@/components/MetricsPanel'
import { TipsPanel } from '@/components/TipsPanel'
import { useQuery } from '@tanstack/react-query'

export const Route = createFileRoute('/jobs/$jobId/results')({
  component: ResultsPage,
})

function ResultsPage() {
  const { jobId } = Route.useParams()

  const { data: results } = useQuery({
    queryKey: ['job-results', jobId],
    queryFn: async () => {
      const res = await fetch(`/api/jobs/${jobId}/results`)
      if (!res.ok) throw new Error('Failed to fetch results')
      return res.json()
    },
  })

  const { data: tracks } = useQuery({
    queryKey: ['job-tracks', jobId],
    queryFn: async () => {
      const res = await fetch(`/api/jobs/${jobId}/tracks`)
      if (!res.ok) throw new Error('Failed to fetch tracks')
      return res.json()
    },
  })

  const { data: jobStatus } = useQuery({
    queryKey: ['job-status', jobId],
    queryFn: async () => {
      const res = await fetch(`/api/jobs/${jobId}`)
      if (!res.ok) throw new Error('Failed to fetch job status')
      return res.json()
    },
  })

  if (!results || !tracks) {
    return <div>Loading results...</div>
  }

  // Get duration from metadata or default to 30 seconds
  const duration = 30 // Default, could be fetched from metadata endpoint

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-gray-900">Analysis Results</h2>

      <div className="bg-white rounded-lg shadow p-6">
        <VideoPlayerWithCanvasOverlay
          jobId={jobId}
          tracks={tracks.frames}
          events={results.events}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <MetricsPanel metrics={results.metrics} />
        <TipsPanel tips={results.tips} />
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <Timeline
          events={results.events}
          duration={duration}
          onSeek={(timestamp) => {
            const video = document.querySelector('video') as HTMLVideoElement
            if (video) {
              video.currentTime = timestamp
            }
          }}
        />
      </div>
    </div>
  )
}

