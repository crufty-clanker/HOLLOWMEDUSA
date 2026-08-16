import { useState } from 'react'
import Editor from '@monaco-editor/react'

const prompts = [
  { id: '1', step: 'requirements', system_prompt: 'You are a product analyst...', version: 1 },
  { id: '2', step: 'architecture', system_prompt: 'You are a distributed systems architect...', version: 1 },
  { id: '3', step: 'code_generation', system_prompt: 'You are a backend engineer...', version: 1 },
]

export default function PromptEditor() {
  const [selectedPrompt, setSelectedPrompt] = useState(prompts[0])
  const [code, setCode] = useState(selectedPrompt.system_prompt)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Prompt Editor</h1>
        <div className="flex gap-2">
          <button className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
            Save
          </button>
          <button className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700">
            Lint
          </button>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-6">
        <div className="col-span-1 bg-white rounded-lg border border-gray-200 p-4">
          <h3 className="font-semibold mb-4">Prompts</h3>
          <div className="space-y-2">
            {prompts.map((prompt) => (
              <button
                key={prompt.id}
                onClick={() => {
                  setSelectedPrompt(prompt)
                  setCode(prompt.system_prompt)
                }}
                className={`w-full text-left px-3 py-2 rounded ${
                  selectedPrompt.id === prompt.id
                    ? 'bg-blue-50 text-blue-700'
                    : 'hover:bg-gray-50'
                }`}
              >
                <p className="font-medium text-sm">{prompt.step}</p>
                <p className="text-xs text-gray-500">v{prompt.version}</p>
              </button>
            ))}
          </div>
        </div>

        <div className="col-span-3">
          <Editor
            height="600px"
            defaultLanguage="markdown"
            value={code}
            onChange={(value) => setCode(value || '')}
            options={{ minimap: { enabled: false } }}
          />
        </div>
      </div>
    </div>
  )
}
