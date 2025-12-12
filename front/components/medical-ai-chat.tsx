"use client"

import { useState } from "react"
import { ChatPanel } from "./chat/chat-panel"
import { AgentGraphPanel } from "./agent-graph/agent-graph-panel"
import { Header } from "./layout/header"
import { mockConversation, mockAgentNodes } from "@/lib/mock-data"
import type { Message, AgentNode } from "@/lib/types"

export function MedicalAIChat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [agentNodes, setAgentNodes] = useState<AgentNode[]>([])
  const [isStreaming, setIsStreaming] = useState(false)
  const [currentStreamingText, setCurrentStreamingText] = useState("")
  const [activeNodeId, setActiveNodeId] = useState<string | null>(null)
  const [conversationIndex, setConversationIndex] = useState(0)

  const simulateConversation = () => {
    if (conversationIndex >= mockConversation.length) {
      setConversationIndex(0)
      setMessages([])
      setAgentNodes([])
      return
    }

    const currentItem = mockConversation[conversationIndex]

    if (currentItem.role === "user") {
      setMessages((prev) => [...prev, currentItem])
      setConversationIndex((prev) => prev + 1)
    } else {
      // Simulate AI streaming response
      setIsStreaming(true)
      const fullText = currentItem.content
      let charIndex = 0

      // Add corresponding agent nodes
      const correspondingNodes = mockAgentNodes.filter((node) => node.messageIndex === conversationIndex)

      correspondingNodes.forEach((node, idx) => {
        setTimeout(() => {
          setAgentNodes((prev) => [...prev, { ...node, status: "running" }])
          setActiveNodeId(node.id)

          // Mark node as complete after delay
          setTimeout(() => {
            setAgentNodes((prev) => prev.map((n) => (n.id === node.id ? { ...n, status: "complete" } : n)))
          }, node.duration)
        }, idx * 800)
      })

      const streamInterval = setInterval(() => {
        if (charIndex < fullText.length) {
          setCurrentStreamingText(fullText.slice(0, charIndex + 1))
          charIndex++
        } else {
          clearInterval(streamInterval)
          setMessages((prev) => [...prev, currentItem])
          setCurrentStreamingText("")
          setIsStreaming(false)
          setActiveNodeId(null)
          setConversationIndex((prev) => prev + 1)
        }
      }, 15)
    }
  }

  const handleSendMessage = (text: string) => {
    simulateConversation()
  }

  const handleReset = () => {
    setMessages([])
    setAgentNodes([])
    setConversationIndex(0)
    setIsStreaming(false)
    setCurrentStreamingText("")
    setActiveNodeId(null)
  }

  return (
    <div className="flex h-screen flex-col bg-background">
      <Header onReset={handleReset} />
      <div className="flex flex-1 min-h-0 flex-col md:flex-row overflow-hidden">
        <ChatPanel
          messages={messages}
          isStreaming={isStreaming}
          currentStreamingText={currentStreamingText}
          onSendMessage={handleSendMessage}
        />
        <AgentGraphPanel nodes={agentNodes} activeNodeId={activeNodeId} />
      </div>
    </div>
  )
}
