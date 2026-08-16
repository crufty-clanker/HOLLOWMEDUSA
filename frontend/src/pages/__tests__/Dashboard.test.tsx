import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@/test/test-utils'
import Dashboard from '@/pages/Dashboard'

describe('Dashboard', () => {
  it('renders the dashboard heading', () => {
    render(<Dashboard />)
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
  })

  it('shows empty state message when no runs', () => {
    render(<Dashboard />)
    expect(screen.getByText('No runs yet. Start a new pipeline run!')).toBeInTheDocument()
  })

  it('renders a New Run button', () => {
    render(<Dashboard />)
    expect(screen.getByRole('button', { name: /new run/i })).toBeInTheDocument()
  })

  it('renders stat cards', () => {
    render(<Dashboard />)
    expect(screen.getByText('Total Runs')).toBeInTheDocument()
    expect(screen.getByText('Successful')).toBeInTheDocument()
    expect(screen.getByText('Failed')).toBeInTheDocument()
  })
})
