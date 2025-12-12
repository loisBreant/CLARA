export interface Message {
  role: "user" | "assistant"
  content: string
  image?: string
  timestamp?: string
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
