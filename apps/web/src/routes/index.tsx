import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { UploadCard } from '@/components/UploadCard'

export const Route = createFileRoute('/')({
  component: Index,
})

function Index() {
  const navigate = useNavigate()

  const handleUploadSuccess = (jobId: string) => {
    navigate({ to: '/jobs/$jobId', params: { jobId } })
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-lg shadow p-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Upload Your Surf Video
        </h2>
        <p className="text-gray-600 mb-8">
          Upload a video of yourself surfing and get personalized coaching tips
          to improve your technique.
        </p>
        <UploadCard onUploadSuccess={handleUploadSuccess} />
      </div>
    </div>
  )
}

