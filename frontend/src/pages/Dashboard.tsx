import { useState } from 'react'

export default function Dashboard() {
  const [runs] = useState<any[]>([])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <button
          onClick={() => alert('Start new run')}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          New Run
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <StatCard label="Total Runs" value={runs.length} />
        <StatCard label="Successful" value={runs.filter((r: any) => r.status === 'completed').length} />
        <StatCard label="Failed" value={runs.filter((r: any) => r.status === 'failed').length} />
      </div>

      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <h2 className="text-lg font-semibold mb-4">Recent Runs</h2>
        {runs.length === 0 ? (
          <p className="text-gray-500">No runs yet. Start a new pipeline run!</p>
        ) : (
          <div className="space-y-2">
            {runs.map((run: any) => (
              <div key={run.id} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                <div>
                  <p className="font-medium">{run.id}</p>
                  <p className="text-sm text-gray-500">{new Date(run.created_at).toLocaleString()}</p>
                </div>
                <span className={`px-2 py-1 rounded text-sm ${
                  run.status === 'completed' ? 'bg-green-100 text-green-700' :
                  run.status === 'failed' ? 'bg-red-100 text-red-700' :
                  'bg-blue-100 text-blue-700'
                }`}>
                  {run.status}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function StatCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <p className="text-sm text-gray-500">{label}</p>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
    </div>
  )
}
