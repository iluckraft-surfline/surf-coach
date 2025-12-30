interface MetricsPanelProps {
  metrics: {
    popUpTime?: number
    turnCount?: number
    averageSpeed?: number
    speedRetention?: number
    smoothness?: number
  }
}

export function MetricsPanel({ metrics }: MetricsPanelProps) {
  const formatMetric = (value: number | undefined, suffix: string = '') => {
    if (value === undefined) return 'N/A'
    return `${value.toFixed(2)}${suffix}`
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Metrics</h3>
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <span className="text-gray-600">Pop-up Time</span>
          <span className="text-lg font-medium text-gray-900">
            {formatMetric(metrics.popUpTime, 's')}
          </span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-gray-600">Turn Count</span>
          <span className="text-lg font-medium text-gray-900">
            {formatMetric(metrics.turnCount)}
          </span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-gray-600">Average Speed</span>
          <span className="text-lg font-medium text-gray-900">
            {formatMetric(metrics.averageSpeed)}
          </span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-gray-600">Speed Retention</span>
          <span className="text-lg font-medium text-gray-900">
            {formatMetric(metrics.speedRetention)}
          </span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-gray-600">Smoothness</span>
          <span className="text-lg font-medium text-gray-900">
            {formatMetric(metrics.smoothness)}
          </span>
        </div>
      </div>
    </div>
  )
}

