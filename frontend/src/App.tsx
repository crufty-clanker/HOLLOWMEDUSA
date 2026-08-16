import { Routes, Route } from 'react-router-dom'

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <h1 className="text-xl font-bold text-gray-900">HollowMedusa</h1>
      </header>
      <main className="p-6">
        <Routes>
          <Route path="/" element={<div>Welcome to HollowMedusa</div>} />
        </Routes>
      </main>
    </div>
  )
}

export default App
