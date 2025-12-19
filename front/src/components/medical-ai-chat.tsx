"use client";

import { useEffect, useState } from "react";
import { fetchApi, uploadFile } from "../lib/api.ts";
import { ChatPanel } from "./chat/chat-panel.tsx";
import { AgentGraphPanel } from "./agent-graph/agent-graph-panel.tsx";
import { Header } from "./layout/header.tsx";
import type {
  AgentData,
  AgentNode,
  AgentResponse,
  AgentsMetrics,
  AgentType,
  Message,
} from "../lib/types.ts";

export function MedicalAIChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [agentNodes, setAgentNodes] = useState<AgentNode[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentStreamingText, setCurrentStreamingText] = useState("");
  const [activeNodeId, setActiveNodeId] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [metrics, setMetrics] = useState<AgentsMetrics | null>(null);

  // Initialize session on component mount
  useEffect(() => {
    const initSession = async () => {
      try {
        const response = await fetchApi("/init-session", "POST");
        const data = await response.json(); // Explicitly parse JSON here
        setSessionId(data.session_id);
      } catch (error) {
        console.error("Failed to initialize session:", error);
      }
    };
    initSession();
  }, []);

  const handleSendMessage = async (text: string, file?: File) => {
    if (!sessionId) {
      console.error("No session ID available. Message not sent.");
      return;
    }

    let imageUrl: string | undefined = undefined;
    let imagePath: string | undefined = undefined;

    if (file) {
      try {
        const uploadResponse = await uploadFile("/upload", file);
        const BACKEND_URL = import.meta.env.VITE_BACKEND_URL ||
          "http://localhost:8000";
        imageUrl = `${BACKEND_URL}${uploadResponse.url}`;
        imagePath = uploadResponse.url;
      } catch (error) {
        console.error("Failed to upload file:", error);
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: `Error: Failed to upload image. ${error}`,
          },
        ]);
        return;
      }
    }

    const userMessage: Message = {
      role: "user",
      content: text,
      image: imageUrl,
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsStreaming(true);
    setCurrentStreamingText("");

    try {
      const response = await fetchApi("/chat", "POST", {
        question: text,
        session_id: sessionId,
        image_url: imagePath,
      });

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error("Failed to get reader from response body.");
      }

      const decoder = new TextDecoder("utf-8");

      let currentSegmentText = "";
      let currentAgentId: string | null = null;
      let currentAgentType: AgentType | undefined = undefined;
      let localAgentsMap: Record<string, AgentData> = {};

      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          break;
        }
        const textChunk = decoder.decode(value, { stream: true });

        try {
          const lines = textChunk.split("\n");
          for (const line of lines) {
            if (!line.trim()) continue;

            const agentResponse: AgentResponse = JSON.parse(line);

            // Update Metrics
            if (agentResponse.metrics) {
              setMetrics(agentResponse.metrics);
              localAgentsMap = agentResponse.metrics.agents;

              // Update Agent Nodes based on metrics
              const newNodes: AgentNode[] = Object.values(
                agentResponse.metrics.agents,
              ).map((agent: AgentData) => {
                // Determine status
                let status: "pending" | "running" | "complete" = "pending";

                // Prioritize completion status
                if (agent.status === "finished" || agent.time_taken > 0) {
                  status = "complete";
                } else if (agent.id === agentResponse.id) {
                  status = "running";
                }

                // Determine parentId (first dependency)
                const parentId = agent.dependencies.length > 0
                  ? agent.dependencies[0]
                  : undefined;

                // Determine children (agents that depend on this one)
                // This is O(N^2) but N is small (number of agents)
                const childrenIds = Object.values(agentResponse.metrics.agents)
                  .filter((other) => other.dependencies.includes(agent.id))
                  .map((other) => other.id);

                return {
                  id: agent.id,
                  name: formatAgentName(agent.type),
                  type: agent.type,
                  description: getAgentDescription(agent.type),
                  status: status,
                  tokens: agent.input_token_count + agent.output_token_count,
                  duration: agent.time_taken * 1000, // s to ms
                  parentId: parentId,
                  childrenIds: childrenIds,
                  messageIndex: messages.length + 1, // Current message index (approximation)
                };
              });

              setAgentNodes(newNodes);
            }

            const chunkAgentId = agentResponse.id;

            // Check for agent switch
            if (chunkAgentId && chunkAgentId !== currentAgentId) {
              // If we have accumulated text for a previous agent, commit it as a message
              if (currentSegmentText) {
                const messageToAdd: Message = {
                  role: "assistant",
                  content: currentSegmentText,
                  agentType: currentAgentType,
                };
                setMessages((prev) => [...prev, messageToAdd]);
                currentSegmentText = "";
                setCurrentStreamingText("");
              }

              currentAgentId = chunkAgentId;
              // Try to resolve type
              if (localAgentsMap[chunkAgentId]) {
                currentAgentType = localAgentsMap[chunkAgentId].type;
              }
            }

            // If we still don't have the type (e.g. metrics arrived late), try update
            if (
              currentAgentId && !currentAgentType &&
              localAgentsMap[currentAgentId]
            ) {
              currentAgentType = localAgentsMap[currentAgentId].type;
            }

            // Update Streaming Text
            if (agentResponse.chunk) {
              currentSegmentText += agentResponse.chunk;
              setCurrentStreamingText(currentSegmentText);
            }

            // Update Active Node ID
            if (agentResponse.id) {
              setActiveNodeId(agentResponse.id);
            }
          }
        } catch (error) {
          console.error("Error parsing stream chunk:", error);
        }
      }

      // Final commit of any remaining text
      if (currentSegmentText) {
        const aiMessage: Message = {
          role: "assistant",
          content: currentSegmentText,
          agentType: currentAgentType,
        };
        setMessages((prev) => [...prev, aiMessage]);
      }

      setActiveNodeId(null); // Reset active node after completion
    } catch (error) {
      console.error("Failed to send message:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Error: Could not get a response. ${error}`,
        },
      ]);
    } finally {
      setIsStreaming(false);
      setCurrentStreamingText("");
    }
  };

  return (
    <div className="flex h-screen flex-col bg-background">
      <Header />
      <div className="flex flex-1 min-h-0 flex-col md:flex-row overflow-hidden">
        <ChatPanel
          messages={messages}
          isStreaming={isStreaming}
          currentStreamingText={currentStreamingText}
          onSendMessage={handleSendMessage}
          sessionId={sessionId}
        />
        <AgentGraphPanel
          nodes={agentNodes}
          activeNodeId={activeNodeId}
          metrics={metrics}
        />
      </div>
    </div>
  );
}

// Helpers for formatting
function formatAgentName(type: string): string {
  return type.charAt(0).toUpperCase() + type.slice(1) + " Agent";
}

function getAgentDescription(type: string): string {
  switch (type) {
    case "planner":
      return "Analyzes the request and creates a step-by-step execution plan.";
    case "executor":
      return "Executes the tasks defined in the plan using available tools.";
    case "reactive":
      return "Reacts to immediate observations or clarifies ambiguities.";
    default:
      return "Performs specialized tasks for the medical analysis.";
  }
}
