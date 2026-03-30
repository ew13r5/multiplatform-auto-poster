import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import CalendarGrid from '../components/Schedule/CalendarGrid'
import type { ScheduleSlot } from '../types/schedule'

const slots: ScheduleSlot[] = [
  { page_id: 'p1', day_of_week: 0, time_utc: '09:00', timezone: 'UTC', enabled: true },
  { page_id: 'p1', day_of_week: 2, time_utc: '14:00', timezone: 'UTC', enabled: true },
  { page_id: 'p2', day_of_week: 0, time_utc: '09:00', timezone: 'UTC', enabled: true },
]

describe('CalendarGrid', () => {
  it('renders 7 day column headers', () => {
    render(<CalendarGrid slots={[]} pageId="p1" onToggle={() => {}} />)
    for (const day of ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']) {
      expect(screen.getByText(day)).toBeDefined()
    }
  })

  it('renders 24 hour labels', () => {
    render(<CalendarGrid slots={[]} pageId="p1" onToggle={() => {}} />)
    expect(screen.getByText('00:00')).toBeDefined()
    expect(screen.getByText('23:00')).toBeDefined()
  })

  it('highlights active slots with blue background', () => {
    const { container } = render(<CalendarGrid slots={slots} pageId="p1" onToggle={() => {}} />)
    const activeCells = container.querySelectorAll('.bg-blue-500')
    expect(activeCells.length).toBe(2)
  })

  it('calls onToggle with day and hour when cell clicked', () => {
    const onToggle = vi.fn()
    const { container } = render(<CalendarGrid slots={[]} pageId="p1" onToggle={onToggle} />)
    // Click first data cell (Mon 00:00) — first row, second td (after hour label)
    const firstRow = container.querySelector('tbody tr')!
    const cells = firstRow.querySelectorAll('td')
    fireEvent.click(cells[1]) // day=0, hour=0
    expect(onToggle).toHaveBeenCalledWith(0, 0)
  })
})
