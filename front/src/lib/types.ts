export interface Message {
  role: "user" | "assistant"
  content: string
  image?: string
  timestamp?: string
  agentType?: AgentType
}

export type AgentType = "planner" | "executor" | "reactive"

export interface AgentData {
  id: string
  type: AgentType
  dependencies: string[]
  input_token_count: number
  output_token_count: number
  time_taken: number
}

export interface AgentsMetrics {
  agents: Record<string, AgentData>
  total_time: number
}

export interface AgentResponse {
  metrics: AgentsMetrics
  id: string
  chunk: string
}

export interface AgentNode {
  id: string
  name: string
  type: AgentType | "orchestrator" | "vision" | "analysis" | "response" | "diagnosis"
  description: string
  status: "pending" | "running" | "complete"
  tokens: number
  duration: number
  parentId?: string
  childrenIds?: string[]
  messageIndex: number
}

// Legacy type for parts of the UI that haven't been fully refactored yet, 
// or computed derived metrics for display.
export interface DisplayMetrics {
  total_input_tokens: number
  total_output_tokens: number
  total_time: number
}