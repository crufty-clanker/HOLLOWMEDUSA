import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@/test/test-utils'
import ThemeToggle from '@/components/ThemeToggle'

describe('ThemeToggle', () => {
  it('renders with correct aria-label', () => {
    render(<ThemeToggle />)
    expect(screen.getByLabelText('Toggle theme')).toBeInTheDocument()
  })

  it('shows moon icon in light theme', () => {
    render(<ThemeToggle />, { theme: 'light' })
    expect(screen.getByRole('button')).toHaveTextContent('🌙')
  })

  it('shows sun icon in dark theme', () => {
    render(<ThemeToggle />, { theme: 'dark' })
    expect(screen.getByRole('button')).toHaveTextContent('☀️')
  })

  it('calls toggleTheme on click', () => {
    const toggleTheme = vi.fn()
    render(<ThemeToggle />, { theme: 'light', toggleTheme })
    fireEvent.click(screen.getByRole('button'))
    expect(toggleTheme).toHaveBeenCalledTimes(1)
  })
})
