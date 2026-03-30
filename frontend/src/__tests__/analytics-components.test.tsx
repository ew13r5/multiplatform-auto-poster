import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import EngagementChart from '../components/Analytics/EngagementChart'
import BestTimeHeatmap from '../components/Analytics/BestTimeHeatmap'
import TopPostsTable from '../components/Analytics/TopPostsTable'
import type { PostEngagement, HeatmapCell } from '../types/analytics'

const posts: PostEngagement[] = [
  { post_id: '1', content_preview: 'Great post about React', page_name: 'Tech Blog', likes: 50, comments: 10, shares: 5, published_at: '2025-01-15T12:00:00Z' },
  { post_id: '2', content_preview: 'Another awesome post', page_name: 'Tech Blog', likes: 30, comments: 20, shares: 10, published_at: '2025-01-16T12:00:00Z' },
]

const cells: HeatmapCell[] = [
  { day: 0, hour: 9, avg_engagement: 10 },
  { day: 2, hour: 14, avg_engagement: 25 },
  { day: 4, hour: 18, avg_engagement: 5 },
]

// Mock ResizeObserver for Recharts ResponsiveContainer
class ResizeObserverMock {
  observe() {}
  unobserve() {}
  disconnect() {}
}
globalThis.ResizeObserver = ResizeObserverMock as unknown as typeof ResizeObserver

describe('EngagementChart', () => {
  it('renders chart container when posts provided', () => {
    const { container } = render(<EngagementChart posts={posts} />)
    expect(container.querySelector('.recharts-responsive-container')).toBeDefined()
  })

  it('shows empty state when no posts', () => {
    render(<EngagementChart posts={[]} />)
    expect(screen.getByText('No engagement data')).toBeDefined()
  })
})

describe('BestTimeHeatmap', () => {
  it('renders 7 day labels', () => {
    render(<BestTimeHeatmap cells={cells} />)
    for (const day of ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']) {
      expect(screen.getByText(day)).toBeDefined()
    }
  })

  it('renders Less/More legend', () => {
    render(<BestTimeHeatmap cells={cells} />)
    expect(screen.getByText('Less')).toBeDefined()
    expect(screen.getByText('More')).toBeDefined()
  })
})

describe('TopPostsTable', () => {
  it('renders rows with engagement data', () => {
    render(<TopPostsTable posts={posts} />)
    expect(screen.getAllByText('Tech Blog').length).toBe(2)
    expect(screen.getByText('50')).toBeDefined()
  })

  it('shows empty state when no posts', () => {
    render(<TopPostsTable posts={[]} />)
    expect(screen.getByText('No posts yet')).toBeDefined()
  })
})
