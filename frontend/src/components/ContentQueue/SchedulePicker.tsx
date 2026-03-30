import { useState } from 'react'
import { Calendar, Clock, X, Zap, Minus, Plus, Globe } from 'lucide-react'

interface SchedulePickerProps {
  value: string // ISO datetime-local string e.g. "2026-03-29T14:30"
  onChange: (value: string) => void
}

function pad(n: number) { return n.toString().padStart(2, '0') }

function formatDateForInput(d: Date) {
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}

function formatTimeForDisplay(h: number, m: number) {
  return `${pad(h)}:${pad(m)}`
}

function addDays(d: Date, n: number) {
  const r = new Date(d)
  r.setDate(r.getDate() + n)
  return r
}

const quickTimes = [
  { label: '09:00', h: 9, m: 0 },
  { label: '12:00', h: 12, m: 0 },
  { label: '15:00', h: 15, m: 0 },
  { label: '18:00', h: 18, m: 0 },
  { label: '20:00', h: 20, m: 0 },
  { label: '21:00', h: 21, m: 0 },
]

export default function SchedulePicker({ value, onChange }: SchedulePickerProps) {
  const [isOpen, setIsOpen] = useState(false)

  const now = new Date()
  const today = formatDateForInput(now)
  const tomorrow = formatDateForInput(addDays(now, 1))

  // Parse current value
  const selectedDate = value ? value.slice(0, 10) : ''
  const selectedHour = value ? parseInt(value.slice(11, 13)) : -1
  const selectedMin = value ? parseInt(value.slice(14, 16)) : 0

  function setDateTime(date: string, h: number, m: number) {
    onChange(`${date}T${pad(h)}:${pad(m)}`)
  }

  function handleDateChange(date: string) {
    if (selectedHour >= 0) {
      onChange(`${date}T${pad(selectedHour)}:${pad(selectedMin)}`)
    } else {
      // Default to next reasonable time
      const nextH = now.getHours() + 1
      onChange(`${date}T${pad(Math.min(nextH, 23))}:00`)
    }
  }

  function handleTimeChange(h: number, m: number) {
    const date = selectedDate || today
    onChange(`${date}T${pad(h)}:${pad(m)}`)
  }

  function adjustMinutes(delta: number) {
    if (!value) return
    const d = new Date(value)
    d.setMinutes(d.getMinutes() + delta)
    onChange(`${formatDateForInput(d)}T${pad(d.getHours())}:${pad(d.getMinutes())}`)
  }

  function handleClear() {
    onChange('')
    setIsOpen(false)
  }

  // Quick presets
  function setQuickPreset(label: string) {
    if (label === 'today_evening') {
      setDateTime(today, 20, 0)
    } else if (label === 'tomorrow_morning') {
      setDateTime(tomorrow, 9, 0)
    } else if (label === 'tomorrow_evening') {
      setDateTime(tomorrow, 18, 0)
    }
    setIsOpen(false)
  }

  // Display text
  const displayText = value
    ? (() => {
        const d = new Date(value)
        const dateStr = d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })
        const timeStr = d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
        return `${dateStr} at ${timeStr}`
      })()
    : null

  return (
    <div className="relative">
      <label className="block text-sm font-medium mb-2">Publish at</label>

      {!isOpen && !value && (
        <button
          type="button"
          onClick={() => setIsOpen(true)}
          className="w-full flex items-center gap-2 border-2 border-dashed border-gray-300 rounded-lg px-4 py-3 text-sm text-gray-500 hover:border-blue-400 hover:text-blue-600 hover:bg-blue-50/50 transition-colors"
        >
          <Calendar size={16} />
          Schedule for later...
        </button>
      )}

      {!isOpen && value && (
        <div className="flex items-center gap-2 bg-blue-50 border border-blue-200 rounded-lg px-4 py-2.5">
          <Clock size={16} className="text-blue-600 shrink-0" />
          <span className="text-sm font-medium text-blue-800 flex-1">{displayText}</span>
          <button type="button" onClick={() => setIsOpen(true)} className="text-xs text-blue-600 hover:text-blue-800 font-medium">
            Change
          </button>
          <button type="button" onClick={handleClear} className="text-blue-400 hover:text-blue-600">
            <X size={14} />
          </button>
        </div>
      )}

      {isOpen && (
        <div className="border rounded-xl bg-white shadow-lg p-4 space-y-4">
          {/* Quick presets */}
          <div>
            <div className="flex items-center gap-1.5 text-xs font-medium text-gray-500 mb-2">
              <Zap size={12} />
              Quick schedule
            </div>
            <div className="flex gap-2 flex-wrap">
              {now.getHours() < 19 && (
                <button type="button" onClick={() => setQuickPreset('today_evening')}
                  className="px-3 py-1.5 text-xs rounded-lg bg-gray-100 hover:bg-blue-100 hover:text-blue-700 transition-colors">
                  Today 20:00
                </button>
              )}
              <button type="button" onClick={() => setQuickPreset('tomorrow_morning')}
                className="px-3 py-1.5 text-xs rounded-lg bg-gray-100 hover:bg-blue-100 hover:text-blue-700 transition-colors">
                Tomorrow 09:00
              </button>
              <button type="button" onClick={() => setQuickPreset('tomorrow_evening')}
                className="px-3 py-1.5 text-xs rounded-lg bg-gray-100 hover:bg-blue-100 hover:text-blue-700 transition-colors">
                Tomorrow 18:00
              </button>
            </div>
          </div>

          <div className="h-px bg-gray-100" />

          {/* Date picker */}
          <div>
            <div className="text-xs font-medium text-gray-500 mb-2">Date</div>
            <div className="flex gap-2 mb-2">
              <button type="button" onClick={() => handleDateChange(today)}
                className={`px-3 py-1.5 text-xs rounded-lg transition-colors ${
                  selectedDate === today ? 'bg-blue-600 text-white' : 'bg-gray-100 hover:bg-gray-200'
                }`}>
                Today
              </button>
              <button type="button" onClick={() => handleDateChange(tomorrow)}
                className={`px-3 py-1.5 text-xs rounded-lg transition-colors ${
                  selectedDate === tomorrow ? 'bg-blue-600 text-white' : 'bg-gray-100 hover:bg-gray-200'
                }`}>
                Tomorrow
              </button>
              <button type="button" onClick={() => handleDateChange(formatDateForInput(addDays(now, 2)))}
                className={`px-3 py-1.5 text-xs rounded-lg transition-colors ${
                  selectedDate === formatDateForInput(addDays(now, 2)) ? 'bg-blue-600 text-white' : 'bg-gray-100 hover:bg-gray-200'
                }`}>
                {addDays(now, 2).toLocaleDateString('en-US', { weekday: 'short' })}
              </button>
            </div>
            <input
              type="date"
              value={selectedDate}
              min={today}
              onChange={(e) => handleDateChange(e.target.value)}
              className="w-full border rounded-lg px-3 py-2 text-sm"
            />
          </div>

          {/* Time picker */}
          <div>
            <div className="text-xs font-medium text-gray-500 mb-2">Time</div>
            <div className="grid grid-cols-6 gap-1.5 mb-2">
              {quickTimes.map((t) => (
                <button
                  key={t.label}
                  type="button"
                  onClick={() => handleTimeChange(t.h, t.m)}
                  className={`py-1.5 text-xs rounded-lg font-medium transition-colors ${
                    selectedHour === t.h && selectedMin === t.m
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                  }`}
                >
                  {t.label}
                </button>
              ))}
            </div>
            <div className="flex items-center gap-2 mb-2">
              <input
                type="time"
                value={selectedHour >= 0 ? formatTimeForDisplay(selectedHour, selectedMin) : ''}
                onChange={(e) => {
                  const [h, m] = e.target.value.split(':').map(Number)
                  if (!isNaN(h)) handleTimeChange(h, m || 0)
                }}
                className="flex-1 border rounded-lg px-3 py-2 text-sm"
              />
            </div>

            {/* Adjust time ±  */}
            {value && (
              <div className="flex items-center gap-1.5">
                <span className="text-xs text-gray-400 mr-1">Adjust:</span>
                <button type="button" onClick={() => adjustMinutes(-60)}
                  className="flex items-center gap-0.5 px-2 py-1 text-xs rounded bg-gray-100 hover:bg-red-50 hover:text-red-600 transition-colors">
                  <Minus size={10} />1h
                </button>
                <button type="button" onClick={() => adjustMinutes(-15)}
                  className="flex items-center gap-0.5 px-2 py-1 text-xs rounded bg-gray-100 hover:bg-red-50 hover:text-red-600 transition-colors">
                  <Minus size={10} />15m
                </button>
                <button type="button" onClick={() => adjustMinutes(15)}
                  className="flex items-center gap-0.5 px-2 py-1 text-xs rounded bg-gray-100 hover:bg-green-50 hover:text-green-600 transition-colors">
                  <Plus size={10} />15m
                </button>
                <button type="button" onClick={() => adjustMinutes(60)}
                  className="flex items-center gap-0.5 px-2 py-1 text-xs rounded bg-gray-100 hover:bg-green-50 hover:text-green-600 transition-colors">
                  <Plus size={10} />1h
                </button>
              </div>
            )}
          </div>

          {/* Timezone info */}
          <div className="flex items-center gap-1.5 bg-gray-50 rounded-lg px-3 py-2">
            <Globe size={12} className="text-gray-400" />
            <span className="text-xs text-gray-500">
              Your timezone: <strong>{Intl.DateTimeFormat().resolvedOptions().timeZone}</strong>
              {' '}(UTC{new Date().getTimezoneOffset() <= 0 ? '+' : ''}{-new Date().getTimezoneOffset() / 60})
            </span>
          </div>

          {/* Actions */}
          <div className="flex justify-between pt-1">
            <button type="button" onClick={handleClear} className="text-xs text-red-500 hover:text-red-700">
              Clear schedule
            </button>
            <button
              type="button"
              onClick={() => setIsOpen(false)}
              disabled={!value}
              className="px-4 py-1.5 text-xs bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              Done
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
