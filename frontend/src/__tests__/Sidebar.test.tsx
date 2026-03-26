import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect } from 'vitest'
import Sidebar from '../components/Layout/Sidebar'

function renderSidebar() {
  return render(
    <MemoryRouter>
      <Sidebar />
    </MemoryRouter>
  )
}

describe('Sidebar', () => {
  it('renders all 5 navigation links', () => {
    renderSidebar()
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
    expect(screen.getByText('Queue')).toBeInTheDocument()
    expect(screen.getByText('Schedule')).toBeInTheDocument()
    expect(screen.getByText('Analytics')).toBeInTheDocument()
    expect(screen.getByText('Settings')).toBeInTheDocument()
  })

  it('each link has an SVG icon', () => {
    const { container } = renderSidebar()
    const links = container.querySelectorAll('a')
    expect(links).toHaveLength(5)
    links.forEach((link) => {
      expect(link.querySelector('svg')).toBeInTheDocument()
    })
  })
})
