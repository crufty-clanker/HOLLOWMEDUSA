import { useState, useEffect, useRef } from 'react'
import type { Run, StepResult } from '../types/api'

export default function PipelineRunner() {
  const [run, setRun] = useState<Run | null>(null)
  const [stepResults, setStepResults] = useState<StepResult[]>([])
  const [status, setStatus] = useState<'idle' | 'running' | 'paused' | 'completed' | 'stopped'>('idle')
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    return () => {
      wsRef.current?.close()
    }
  }, [])

  const startRun = async () => {
    const resp = await fetch('/api/v1/runs/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ graph_id: 'default' }),
    })
    const data = await resp.json()
    setRun(data)
    setStatus('running')

    // Connect WebSocket
    const ws = new WebSocket(`ws://${window.location.host}/runs/${data.id}/events`)
    wsRef.current = ws
    ws.onmessage = (e) => {
      const event = JSON.parse(e.data)
      if (event.step_results) {
        setStepResults(event.step_results)
      }
    }
  }

  const stopRun = async () => {
    if (!run) return
    await fetch(`/api/v1/runs/${run.id}/stop`, { method: 'POST' })
    setStatus('stopped')
    wsRef.current?.close()
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Pipeline Runner</h1>
        <div className="flex gap-2">
          <button
            onClick={startRun}
            disabled={status === 'running'}
            className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
          >
            Start
          </button>
          <button
            onClick={stopRun}
            disabled={status !== 'running'}
            className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50"
          >
            Stop
          </button>
        </div>
      </div>

      {status === 'running' && (
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
            <span className="font-medium">Running: {run?.id}</span>
          </div>
          <div className="space-y-2">
            {stepResults.map((step: StepResult, idx: number) => (
              <div key={idx} className="flex items-center gap-2 p-2 bg-gray-50 rounded">
                <span className={`w-2 h-2 rounded-full ${
                  step.status === 'succeeded' ? 'bg-green-500' :
                  step.status === 'failed' ? 'bg-red-500' :
                  'bg-yellow-500 animate-pulse'
                }`}></span>
                <span className="text-sm">{step.step}</span>
                <span className="text-xs text-gray-500 ml-auto">{step.status}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {status === 'completed' && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <p className="text-green-700 font-medium">Pipeline completed successfully!</p>
        </div>
      )}
    </div>
  )
}
