import { createFileRoute } from '@tanstack/react-router'
import { JobProgress } from '@/components/JobProgress'

export const Route = createFileRoute('/jobs/$jobId')({
  component: JobStatusPage,
})

function JobStatusPage() {
  const { jobId } = Route.useParams()

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-lg shadow p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          Processing Your Video
        </h2>
        <JobProgress jobId={jobId} />
      </div>
    </div>
  )
}

