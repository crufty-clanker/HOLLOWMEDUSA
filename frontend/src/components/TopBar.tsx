export default function TopBar() {
  return (
    <header className="bg-white border-b border-gray-200 px-6 py-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">
          Pipeline Orchestration
        </h2>
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-500">v0.3.0</span>
        </div>
      </div>
    </header>
  )
}
