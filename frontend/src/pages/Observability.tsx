export default function Observability() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Observability</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h3 className="text-sm font-medium text-gray-500">Total Tokens</h3>
          <p className="text-2xl font-bold text-gray-900">0</p>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h3 className="text-sm font-medium text-gray-500">Estimated Cost</h3>
          <p className="text-2xl font-bold text-gray-900">$0.00</p>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h3 className="text-sm font-medium text-gray-500">Avg Latency</h3>
          <p className="text-2xl font-bold text-gray-900">0ms</p>
        </div>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <h2 className="text-lg font-semibold mb-4">Token Usage by Step</h2>
        <div className="h-64 flex items-center justify-center text-gray-500">
          Chart placeholder
        </div>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <h2 className="text-lg font-semibold mb-4">Error Log</h2>
        <div className="space-y-2">
          <p className="text-gray-500 text-sm">No errors recorded.</p>
        </div>
      </div>
    </div>
  )
}
