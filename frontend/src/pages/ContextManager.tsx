import { useState } from 'react'

const contexts = [
  { id: '1', name: 'Python Backend', description: 'Python best practices', steps: ['code_generation'], files: ['python-style-guide.md'] },
  { id: '2', name: 'React Frontend', description: 'React patterns', steps: ['code_generation'], files: ['react-patterns.md'] },
]

export default function ContextManager() {
  const [contextsList] = useState(contexts)
  const [showAdd, setShowAdd] = useState(false)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Context Manager</h1>
        <button
          onClick={() => setShowAdd(!showAdd)}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Add Context
        </button>
      </div>

      {showAdd && (
        <div className="bg-white p-4 rounded-lg border border-gray-200 space-y-4">
          <h3 className="font-semibold">Add New Context</h3>
          <input type="text" placeholder="Name" className="w-full px-3 py-2 border rounded" />
          <textarea placeholder="Description" className="w-full px-3 py-2 border rounded" rows={3} />
          <div>
            <label className="block text-sm font-medium mb-2">Steps</label>
            <div className="space-y-2">
              {['requirements', 'architecture', 'code_generation', 'testing'].map(step => (
                <label key={step} className="flex items-center gap-2">
                  <input type="checkbox" className="rounded" />
                  <span className="text-sm">{step}</span>
                </label>
              ))}
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Files</label>
            <input type="file" multiple className="w-full" />
          </div>
          <button className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700">
            Save
          </button>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {contextsList.map((ctx) => (
          <div key={ctx.id} className="bg-white rounded-lg border border-gray-200 p-4">
            <h3 className="font-semibold text-lg">{ctx.name}</h3>
            <p className="text-sm text-gray-500 mb-2">{ctx.description}</p>
            <div className="space-y-1">
              <p className="text-xs font-medium text-gray-500">Steps:</p>
              <div className="flex flex-wrap gap-1">
                {ctx.steps.map(step => (
                  <span key={step} className="px-2 py-1 bg-gray-100 text-xs rounded">
                    {step}
                  </span>
                ))}
              </div>
            </div>
            <div className="mt-3">
              <p className="text-xs font-medium text-gray-500 mb-1">Files:</p>
              <ul className="text-xs text-gray-600 space-y-1">
                {ctx.files.map(file => (
                  <li key={file}>• {file}</li>
                ))}
              </ul>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
