export interface Message {
  role: "user" | "assistant"
  content: string
  image?: string
  timestamp?: string
}

export interface AgentMetrics {
  input_token_count: number
  output_token_count: number
  current_time_taken: number
  total_time_taken: number
  current_input_token_count: number
}

export interface AgentResponse {
  metrics: AgentMetrics
  chunk: string
}

export interface AgentNode {
  id: string
  name: string
  type: "orchestrator" | "vision" | "analysis" | "response" | "diagnosis"
  description: string
  status: "pending" | "running" | "complete"
  tokens: number
  duration: number
  parentId?: string
  childrenIds?: string[]
  messageIndex: number
}
