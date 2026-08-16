export type StepStatus = 'pending' | 'running' | 'succeeded' | 'failed' | 'skipped'
export type RunStatus = 'pending' | 'running' | 'completed' | 'failed' | 'stopped'

export interface PipelineState {
  requirements?: Record<string, any>
  architecture?: Record<string, any>
  prompts: Record<string, string>
  code: Record<string, string>
  test_results: any[]
  review?: Record<string, any>
  documentation?: string
  errors: string[]
  metadata: Record<string, any>
}

export interface AgentConfig {
  id: string
  step: string
  harness: string
  system_prompt: string
  primary_model: string
  fallback_models: string[]
  context_ids: string[]
}

export interface ModelConfig {
  id: string
  provider: 'openai' | 'anthropic' | 'ollama'
  model_name: string
  api_key?: string
  base_url?: string
  rate_limit?: number
  timeout: number
}

export interface ContextConfig {
  id: string
  name: string
  description: string
  files: string[]
  steps: string[]
}

export interface Run {
  id: string
  status: RunStatus
  state: PipelineState
  created_at: string
  updated_at: string
}
