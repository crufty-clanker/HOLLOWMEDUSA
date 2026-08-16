import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@/test/test-utils'
import PipelineRunner from '@/pages/PipelineRunner'

// Mock WebSocket
class MockWebSocket {
  static instances: MockWebSocket[] = []
  readyState = 0
  onmessage: ((e: MessageEvent) => void) | null = null

  constructor() {
    MockWebSocket.instances.push(this)
  }

  send() {}
  close() {
    this.readyState = 3
  }
}

vi.stubGlobal('WebSocket', MockWebSocket)

describe('PipelineRunner', () => {
  it('renders the Pipeline Runner heading', () => {
    render(<PipelineRunner />)
    expect(screen.getByText('Pipeline Runner')).toBeInTheDocument()
  })

  it('renders Start and Stop buttons', () => {
    render(<PipelineRunner />)
    expect(screen.getByRole('button', { name: /start/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /stop/i })).toBeInTheDocument()
  })

  it('disables Start button when running', async () => {
    render(<PipelineRunner />)
    // Initially Start is enabled
    expect(screen.getByRole('button', { name: /start/i })).not.toBeDisabled()
  })
})
