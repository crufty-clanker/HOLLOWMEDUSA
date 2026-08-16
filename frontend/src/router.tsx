import { createBrowserRouter } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import GraphEditor from './pages/GraphEditor'
import ModelConfig from './pages/ModelConfig'
import PromptEditor from './pages/PromptEditor'
import ContextManager from './pages/ContextManager'
import PipelineRunner from './pages/PipelineRunner'
import Observability from './pages/Observability'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      { index: true, element: <Dashboard /> },
      { path: 'graph', element: <GraphEditor /> },
      { path: 'models', element: <ModelConfig /> },
      { path: 'prompts', element: <PromptEditor /> },
      { path: 'contexts', element: <ContextManager /> },
      { path: 'runner', element: <PipelineRunner /> },
      { path: 'observability', element: <Observability /> },
    ],
  },
])
