import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { timeAgo } from './timeAgo'

describe('timeAgo', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-03-26T12:00:00Z'))
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('returns "just now" for dates within 60 seconds', () => {
    expect(timeAgo('2026-03-26T11:59:31Z')).toBe('just now')
  })

  it('returns "5 minutes ago"', () => {
    expect(timeAgo('2026-03-26T11:55:00Z')).toBe('5 minutes ago')
  })

  it('returns "1 minute ago" (singular)', () => {
    expect(timeAgo('2026-03-26T11:59:00Z')).toBe('1 minute ago')
  })

  it('returns "3 hours ago"', () => {
    expect(timeAgo('2026-03-26T09:00:00Z')).toBe('3 hours ago')
  })

  it('returns "1 hour ago" (singular)', () => {
    expect(timeAgo('2026-03-26T11:00:00Z')).toBe('1 hour ago')
  })

  it('returns "2 days ago"', () => {
    expect(timeAgo('2026-03-24T12:00:00Z')).toBe('2 days ago')
  })

  it('returns "1 day ago" (singular)', () => {
    expect(timeAgo('2026-03-25T12:00:00Z')).toBe('1 day ago')
  })

  it('returns "Never" for null', () => {
    expect(timeAgo(null)).toBe('Never')
  })

  it('returns "Never" for undefined', () => {
    expect(timeAgo(undefined)).toBe('Never')
  })
})
