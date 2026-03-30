import type { HeatmapCell } from '../../types/analytics'

interface BestTimeHeatmapProps {
  cells: HeatmapCell[]
}

const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
const hours = Array.from({ length: 24 }, (_, i) => i)

const colorScale = [
  'bg-gray-100',
  'bg-blue-100',
  'bg-blue-200',
  'bg-blue-400',
  'bg-blue-500',
  'bg-blue-700',
]

function getColorClass(value: number, max: number): string {
  if (max === 0 || value === 0) return colorScale[0]
  const idx = Math.min(Math.ceil((value / max) * 5), 5)
  return colorScale[idx]
}

export default function BestTimeHeatmap({ cells }: BestTimeHeatmapProps) {
  const cellMap = new Map(cells.map((c) => [`${c.day}-${c.hour}`, c.avg_engagement]))
  const maxVal = cells.length > 0 ? Math.max(...cells.map((c) => c.avg_engagement)) : 0

  return (
    <div className="overflow-x-auto">
      {/* Hour labels */}
      <div className="flex gap-[2px] mb-[2px] ml-10">
        {hours.map((h) => (
          <div key={h} className="flex-1 min-w-[18px] text-[10px] text-center text-gray-400">
            {h % 3 === 0 ? `${h}` : ''}
          </div>
        ))}
      </div>

      {/* Grid */}
      {days.map((dayName, day) => (
        <div key={day} className="flex gap-[2px] mb-[2px]">
          <div className="w-10 text-xs text-gray-500 flex items-center justify-end pr-2 shrink-0">{dayName}</div>
          {hours.map((hour) => {
            const val = cellMap.get(`${day}-${hour}`) ?? 0
            return (
              <div
                key={hour}
                className={`flex-1 min-w-[18px] h-5 rounded-sm transition-colors ${getColorClass(val, maxVal)}`}
                title={`${dayName} ${hour}:00 — ${val.toFixed(1)}`}
              />
            )
          })}
        </div>
      ))}

      {/* Legend */}
      <div className="flex items-center gap-1.5 mt-3 ml-10 text-[11px] text-gray-400">
        <span>Less</span>
        {colorScale.map((cls, i) => (
          <div key={i} className={`w-3.5 h-3.5 rounded-sm ${cls}`} />
        ))}
        <span>More</span>
      </div>
    </div>
  )
}
