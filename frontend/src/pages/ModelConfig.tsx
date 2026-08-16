import { useState } from 'react'

const providers = [
  { id: 'openai/gpt-4o', provider: 'openai', model_name: 'gpt-4o' },
  { id: 'anthropic/claude-sonnet', provider: 'anthropic', model_name: 'claude-sonnet-4-20250514' },
  { id: 'ollama/llama3', provider: 'ollama', model_name: 'llama3' },
]

export default function ModelConfig() {
  const [models] = useState(providers)
  const [showAdd, setShowAdd] = useState(false)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Model Configuration</h1>
        <button
          onClick={() => setShowAdd(!showAdd)}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Add Model
        </button>
      </div>

      {showAdd && (
        <div className="bg-white p-4 rounded-lg border border-gray-200 space-y-4">
          <h3 className="font-semibold">Add New Model</h3>
          <input type="text" placeholder="Model ID" className="w-full px-3 py-2 border rounded" />
          <select className="w-full px-3 py-2 border rounded">
            <option value="openai">OpenAI</option>
            <option value="anthropic">Anthropic</option>
            <option value="ollama">Ollama</option>
          </select>
          <input type="text" placeholder="Model Name" className="w-full px-3 py-2 border rounded" />
          <input type="password" placeholder="API Key" className="w-full px-3 py-2 border rounded" />
          <button className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700">
            Save
          </button>
        </div>
      )}

      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Provider</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Model</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {models.map((model) => (
              <tr key={model.id}>
                <td className="px-6 py-4 text-sm font-medium text-gray-900">{model.id}</td>
                <td className="px-6 py-4 text-sm text-gray-500">{model.provider}</td>
                <td className="px-6 py-4 text-sm text-gray-500">{model.model_name}</td>
                <td className="px-6 py-4 text-sm">
                  <button className="text-blue-600 hover:text-blue-800 mr-4">Edit</button>
                  <button className="text-red-600 hover:text-red-800">Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
