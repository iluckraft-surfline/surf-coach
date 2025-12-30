interface Event {
  type: string
  timestamp: number
  confidence: number
}

interface TimelineProps {
  events: Event[]
  duration: number
  onSeek: (timestamp: number) => void
}

export function Timeline({ events, duration, onSeek }: TimelineProps) {
  const getEventColor = (type: string) => {
    return type === 'pop-up' ? 'bg-red-500' : 'bg-yellow-500'
  }

  const getEventLabel = (type: string) => {
    return type === 'pop-up' ? 'Pop-up' : 'Turn'
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900">Timeline</h3>
      <div className="relative h-16 bg-gray-100 rounded-lg">
        {events.map((event, index) => {
          const position = (event.timestamp / duration) * 100
          return (
            <button
              key={index}
              onClick={() => onSeek(event.timestamp)}
              className={`absolute top-0 h-full w-1 ${getEventColor(
                event.type
              )} hover:opacity-80 transition-opacity`}
              style={{ left: `${position}%` }}
              title={`${getEventLabel(event.type)} at ${event.timestamp.toFixed(
                1
              )}s`}
            />
          )
        })}
        <div className="absolute bottom-0 left-0 right-0 flex justify-between text-xs text-gray-500 px-2">
          <span>0s</span>
          <span>{duration.toFixed(1)}s</span>
        </div>
      </div>
      <div className="flex flex-wrap gap-4">
        {events.map((event, index) => (
          <div
            key={index}
            className="flex items-center gap-2 text-sm"
          >
            <div
              className={`w-3 h-3 rounded-full ${getEventColor(event.type)}`}
            />
            <span className="text-gray-700">
              {getEventLabel(event.type)} at {event.timestamp.toFixed(1)}s
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}

