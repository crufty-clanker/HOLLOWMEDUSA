import ReactFlow, {
  type Connection,
  addEdge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
} from 'reactflow'
import 'reactflow/dist/style.css'

const initialNodes = [
  { id: '1', type: 'input', data: { label: 'Requirements' }, position: { x: 250, y: 0 } },
  { id: '2', data: { label: 'Architecture' }, position: { x: 250, y: 100 } },
  { id: '3', data: { label: 'Code Generation' }, position: { x: 250, y: 200 } },
  { id: '4', type: 'output', data: { label: 'Documentation' }, position: { x: 250, y: 300 } },
]

const initialEdges = [
  { id: 'e1-2', source: '1', target: '2' },
  { id: 'e2-3', source: '2', target: '3' },
  { id: 'e3-4', source: '3', target: '4' },
]

export default function GraphEditor() {
  const [nodes, , onNodesChange] = useNodesState(initialNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges)

  const onConnect = (params: Connection) => setEdges((eds) => addEdge(params, eds))

  return (
    <div className="h-[calc(100vh-12rem)] bg-white rounded-lg border border-gray-200">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        fitView
      >
        <Controls />
        <MiniMap />
        <Background />
      </ReactFlow>
    </div>
  )
}
