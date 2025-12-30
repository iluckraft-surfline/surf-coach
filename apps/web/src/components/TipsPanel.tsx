interface Tip {
  id: string
  message: string
  confidence: number
  timestamp?: number
  impact: string
}

interface TipsPanelProps {
  tips: Tip[]
}

export function TipsPanel({ tips }: TipsPanelProps) {
  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'high':
        return 'border-red-500 bg-red-50'
      case 'medium':
        return 'border-yellow-500 bg-yellow-50'
      case 'low':
        return 'border-blue-500 bg-blue-50'
      default:
        return 'border-gray-500 bg-gray-50'
    }
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Coaching Tips
      </h3>
      <div className="space-y-4">
        {tips.length === 0 ? (
          <p className="text-gray-500 text-sm">No tips available</p>
        ) : (
          tips.map((tip) => (
            <div
              key={tip.id}
              className={`border-l-4 p-4 rounded ${getImpactColor(tip.impact)}`}
            >
              <div className="flex items-start justify-between mb-2">
                <span className="text-xs font-medium text-gray-600 uppercase">
                  {tip.impact} impact
                </span>
                {tip.timestamp !== undefined && (
                  <span className="text-xs text-gray-500">
                    {tip.timestamp.toFixed(1)}s
                  </span>
                )}
              </div>
              <p className="text-gray-900">{tip.message}</p>
              <div className="mt-2 flex items-center gap-2">
                <span className="text-xs text-gray-500">Confidence:</span>
                <div className="flex-1 bg-gray-200 rounded-full h-1.5">
                  <div
                    className="bg-blue-600 h-1.5 rounded-full"
                    style={{ width: `${tip.confidence * 100}%` }}
                  />
                </div>
                <span className="text-xs text-gray-500">
                  {(tip.confidence * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

