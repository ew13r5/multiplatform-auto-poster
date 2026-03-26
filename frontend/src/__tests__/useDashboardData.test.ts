import { renderHook, waitFor, act } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('../api/health', () => ({
  getHealth: vi.fn(),
  getLog: vi.fn(),
}))
vi.mock('../api/pages', () => ({
  getPages: vi.fn(),
}))

import { getHealth, getLog } from '../api/health'
import { getPages } from '../api/pages'
import { useDashboardData } from '../hooks/useDashboardData'

const mockHealth = {
  status: 'healthy',
  checks: { db: true, redis: true, minio: true },
  mode: 'development',
}

const mockPages = [
  {
    id: '1',
    fb_page_id: 'fb1',
    name: 'Test Page',
    token_status: 'configured' as const,
    queued_count: 3,
    last_published_at: new Date().toISOString(),
  },
]

const mockLogResponse = {
  entries: [
    {
      attempted_at: new Date().toISOString(),
      page_name: 'Test Page',
      content_preview: 'Hello world',
      result: 'success',
      retry_count: 0,
    },
  ],
  total: 1,
}

describe('useDashboardData', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('returns loading=true initially', () => {
    vi.mocked(getHealth).mockReturnValue(new Promise(() => {}))
    vi.mocked(getPages).mockReturnValue(new Promise(() => {}))
    vi.mocked(getLog).mockReturnValue(new Promise(() => {}))

    const { result } = renderHook(() => useDashboardData())
    expect(result.current.loading).toBe(true)
  })

  it('returns data after all APIs resolve', async () => {
    vi.mocked(getHealth).mockResolvedValue(mockHealth)
    vi.mocked(getPages).mockResolvedValue(mockPages)
    vi.mocked(getLog).mockResolvedValue(mockLogResponse)

    const { result } = renderHook(() => useDashboardData())
    await waitFor(() => expect(result.current.loading).toBe(false))

    expect(result.current.health).toEqual(mockHealth)
    expect(result.current.pages).toHaveLength(1)
    expect(result.current.logEntries).toHaveLength(1)
    expect(result.current.error).toBeNull()
  })

  it('returns error when API rejects', async () => {
    vi.mocked(getHealth).mockRejectedValue(new Error('Network failure'))
    vi.mocked(getPages).mockResolvedValue(mockPages)
    vi.mocked(getLog).mockResolvedValue(mockLogResponse)

    const { result } = renderHook(() => useDashboardData())
    await waitFor(() => expect(result.current.loading).toBe(false))

    expect(result.current.error).toBe('Network failure')
  })

  it('refetch() re-triggers all fetches', async () => {
    vi.mocked(getHealth).mockResolvedValue(mockHealth)
    vi.mocked(getPages).mockResolvedValue(mockPages)
    vi.mocked(getLog).mockResolvedValue(mockLogResponse)

    const { result } = renderHook(() => useDashboardData())
    await waitFor(() => expect(result.current.loading).toBe(false))

    act(() => { result.current.refetch() })
    await waitFor(() => expect(result.current.loading).toBe(false))

    expect(vi.mocked(getHealth)).toHaveBeenCalledTimes(2)
    expect(vi.mocked(getPages)).toHaveBeenCalledTimes(2)
    expect(vi.mocked(getLog)).toHaveBeenCalledTimes(2)
  })
})
