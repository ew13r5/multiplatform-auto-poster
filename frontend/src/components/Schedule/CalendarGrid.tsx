import type { ScheduleSlot } from '../../types/schedule'

interface CalendarGridProps {
  slots: ScheduleSlot[]
  pageId: string
  onToggle: (day: number, hour: number) => void
}

const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

export default function CalendarGrid({ slots, pageId, onToggle }: CalendarGridProps) {
  const activeSet = new Set(
    slots
      .filter((s) => s.page_id === pageId && s.enabled)
      .map((s) => `${s.day_of_week}-${s.time_utc.slice(0, 2)}`),
  )

  function isActive(day: number, hour: number) {
    return activeSet.has(`${day}-${hour.toString().padStart(2, '0')}`)
  }

  const dayCounts = days.map((_, i) => {
    let count = 0
    for (let h = 0; h < 24; h++) {
      if (isActive(i, h)) count++
    }
    return count
  })

  return (
    <div className="overflow-x-auto">
      <table className="border-collapse">
        <thead>
          <tr>
            <th className="w-16 text-xs text-gray-500 text-left p-1" />
            {days.map((d) => (
              <th key={d} className="w-10 text-xs font-medium text-gray-700 text-center p-1">
                {d}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {Array.from({ length: 24 }, (_, hour) => (
            <tr key={hour}>
              <td className="text-xs text-gray-500 pr-2 text-right">
                {hour.toString().padStart(2, '0')}:00
              </td>
              {days.map((_, day) => {
                const active = isActive(day, hour)
                return (
                  <td
                    key={day}
                    onClick={() => onToggle(day, hour)}
                    className={`w-10 h-8 text-center text-xs cursor-pointer border border-gray-200 ${
                      active
                        ? 'bg-blue-500 text-white hover:bg-blue-600'
                        : 'bg-gray-50 hover:bg-gray-100'
                    }`}
                  />
                )
              })}
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr>
            <td className="text-xs text-gray-500 pr-2 text-right">Slots</td>
            {dayCounts.map((count, i) => (
              <td key={i} className="text-xs text-center text-gray-500 p-1">
                {count}
              </td>
            ))}
          </tr>
        </tfoot>
      </table>
    </div>
  )
}
