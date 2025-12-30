import { useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from '@tanstack/react-router'

interface JobProgressProps {
  jobId: string
}

export function JobProgress({ jobId }: JobProgressProps) {
  const navigate = useNavigate()

  const { data: status, isLoading } = useQuery({
    queryKey: ['job-status', jobId],
    queryFn: async () => {
      const res = await fetch(`/api/jobs/${jobId}`)
      if (!res.ok) throw new Error('Failed to fetch job status')
      return res.json()
    },
    refetchInterval: (query) => {
      const data = query.state.data
      if (data?.status === 'completed') {
        navigate({ to: '/jobs/$jobId/results', params: { jobId } })
        return false
      }
      if (data?.status === 'failed') {
        return false
      }
      return 1000 // Poll every 1 second
    },
  })

  if (isLoading) {
    return <div>Loading...</div>
  }

  const progressPercent = Math.round((status?.progress || 0) * 100)

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-gray-700">
          Status: {status?.status || 'pending'}
        </span>
        <span className="text-sm text-gray-500">{progressPercent}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2.5">
        <div
          className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
          style={{ width: `${progressPercent}%` }}
        />
      </div>
      {status?.error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800 text-sm">{status.error}</p>
        </div>
      )}
      {status?.status === 'processing' && (
        <p className="text-sm text-gray-600">
          Analyzing your video... This may take a minute.
        </p>
      )}
    </div>
  )
}

