import { useMemo } from 'react'
import { Clock, AlertCircle, CheckCircle2 } from 'lucide-react'
import type { Post } from '../../types/post'

interface WeekCalendarProps {
  posts: Post[]
  weekStart: Date
  pageMap: Map<string, string>
  platformMap?: Map<string, string>
  onPostClick: (post: Post) => void
  onSlotClick: (date: Date) => void
}

const hours = Array.from({ length: 24 }, (_, i) => i) // 0:00 - 23:00
const dayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

const platformColors: Record<string, string> = {
  telegram: 'border-l-[#26A5E4] bg-sky-50',
  twitter: 'border-l-black bg-gray-50',
  facebook: 'border-l-[#1877F2] bg-blue-50',
}

const statusIcons = {
  queued: { icon: Clock, cls: 'text-blue-500' },
  published: { icon: CheckCircle2, cls: 'text-green-500' },
  failed: { icon: AlertCircle, cls: 'text-red-500' },
}

function getWeekDays(start: Date): Date[] {
  return Array.from({ length: 7 }, (_, i) => {
    const d = new Date(start)
    d.setDate(d.getDate() + i)
    return d
  })
}

function isSameDay(a: Date, b: Date) {
  return a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() && a.getDate() === b.getDate()
}

function isToday(d: Date) {
  return isSameDay(d, new Date())
}

export default function WeekCalendar({ posts, weekStart, pageMap, platformMap, onPostClick, onSlotClick }: WeekCalendarProps) {
  const days = useMemo(() => getWeekDays(weekStart), [weekStart])

  const postsByDayHour = useMemo(() => {
    const map = new Map<string, Post[]>()
    for (const post of posts) {
      if (!post.scheduled_at) continue
      const d = new Date(post.scheduled_at)
      const dayIdx = days.findIndex((day) => isSameDay(day, d))
      if (dayIdx === -1) continue
      const hour = d.getHours()
      const key = `${dayIdx}-${hour}`
      if (!map.has(key)) map.set(key, [])
      map.get(key)!.push(post)
    }
    return map
  }, [posts, days])

  const now = new Date()
  const nowDayIdx = days.findIndex((d) => isSameDay(d, now))
  const nowMinutes = now.getHours() * 60 + now.getMinutes()

  return (
    <div className="overflow-x-auto">
      <div className="min-w-[700px]">
        {/* Header */}
        <div className="grid grid-cols-[60px_repeat(7,1fr)] border-b sticky top-0 bg-white z-10">
          <div className="p-2" />
          {days.map((day, i) => (
            <div
              key={i}
              className={`p-2 text-center border-l ${isToday(day) ? 'bg-blue-50' : ''}`}
            >
              <div className="text-xs text-gray-500 font-medium">{dayNames[i]}</div>
              <div className={`text-lg font-bold mt-0.5 ${
                isToday(day)
                  ? 'bg-blue-600 text-white rounded-full w-8 h-8 flex items-center justify-center mx-auto'
                  : 'text-gray-800'
              }`}>
                {day.getDate()}
              </div>
            </div>
          ))}
        </div>

        {/* Time grid */}
        <div className="relative">
          {hours.map((hour) => (
            <div key={hour} className="grid grid-cols-[60px_repeat(7,1fr)] min-h-[64px]">
              <div className="text-xs text-gray-400 text-right pr-3 pt-1 font-medium">
                {hour.toString().padStart(2, '0')}:00
              </div>
              {days.map((day, dayIdx) => {
                const cellPosts = postsByDayHour.get(`${dayIdx}-${hour}`) || []
                const isPast = day < now && !isToday(day)
                return (
                  <div
                    key={dayIdx}
                    onClick={() => {
                      const d = new Date(day)
                      d.setHours(hour, 0, 0, 0)
                      onSlotClick(d)
                    }}
                    className={`border-l border-t p-0.5 cursor-pointer transition-colors hover:bg-blue-50/50 ${
                      isToday(day) ? 'bg-blue-50/30' : ''
                    } ${isPast ? 'opacity-60' : ''}`}
                  >
                    {cellPosts.map((post) => {
                      const time = new Date(post.scheduled_at!)
                      const platform = platformMap?.get(post.page_id) || 'telegram'
                      const colorCls = platformColors[platform] || 'border-l-gray-400 bg-gray-50'
                      const stInfo = statusIcons[post.status as keyof typeof statusIcons]
                      const StIcon = stInfo?.icon || Clock

                      return (
                        <div
                          key={post.id}
                          onClick={(e) => { e.stopPropagation(); onPostClick(post) }}
                          className={`rounded-md px-2 py-1 text-xs border-l-[3px] shadow-sm hover:shadow-md transition-shadow cursor-pointer mb-0.5 ${colorCls}`}
                        >
                          <div className="flex items-center gap-1">
                            <StIcon size={10} className={stInfo?.cls || 'text-gray-400'} />
                            <span className="font-medium">
                              {time.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}
                            </span>
                          </div>
                          <div className="truncate text-gray-700 mt-0.5">
                            {post.content_text.slice(0, 40)}
                          </div>
                          <div className="text-gray-400 truncate">
                            {pageMap.get(post.page_id) || ''}
                          </div>
                        </div>
                      )
                    })}
                  </div>
                )
              })}
            </div>
          ))}

          {/* Current time indicator */}
          {nowDayIdx >= 0 && (
            <div
              className="absolute left-[60px] right-0 pointer-events-none z-10"
              style={{ top: `${(nowMinutes / (24 * 60)) * 100}%` }}
            >
              <div className="relative">
                <div className="absolute -left-1.5 -top-1.5 w-3 h-3 rounded-full bg-red-500" />
                <div className="h-0.5 bg-red-500 w-full" />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
