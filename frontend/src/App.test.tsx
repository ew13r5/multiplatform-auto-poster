import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import App from './App'

describe('App', () => {
  it('renders dashboard page at root', () => {
    render(<App />)
    const elements = screen.getAllByText('Dashboard')
    expect(elements.length).toBeGreaterThanOrEqual(1)
  })

  it('renders sidebar navigation', () => {
    render(<App />)
    expect(screen.getByText('Queue')).toBeInTheDocument()
    expect(screen.getByText('Schedule')).toBeInTheDocument()
    expect(screen.getByText('Analytics')).toBeInTheDocument()
    expect(screen.getByText('Settings')).toBeInTheDocument()
  })

  it('shows development mode banner', () => {
    render(<App />)
    expect(screen.getByText(/Development Mode/)).toBeInTheDocument()
  })
})
