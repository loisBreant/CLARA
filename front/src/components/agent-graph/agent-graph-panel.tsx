"use client"

import { useState } from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { MermaidGraph } from "./mermaid-graph"
import { AgentNodeList } from "./agent-node-list"
import { MetricsPanel } from "./metrics-panel"
import { GitBranch, List, BarChart3 } from "lucide-react"
import type { AgentNode, AgentMetrics } from "@/lib/types"

interface AgentGraphPanelProps {
  nodes: AgentNode[]
  activeNodeId: string | null
  metrics: AgentMetrics | null
}

export function AgentGraphPanel({ nodes, activeNodeId, metrics }: AgentGraphPanelProps) {
  const [selectedTab, setSelectedTab] = useState("graph")

  const totalTokens = nodes.reduce((sum, node) => sum + node.tokens, 0)
  const totalTime = nodes.reduce((sum, node) => sum + node.duration, 0)
  const completedNodes = nodes.filter((n) => n.status === "complete").length

  return (
    <div className="flex flex-1 min-w-0 min-h-0 flex-col bg-card/50">
      <div className="flex items-center justify-between border-b border-border px-6 py-4">
        <div>
          <h2 className="text-sm font-semibold text-foreground">Agent Workflow</h2>
          <p className="text-xs text-muted-foreground">Real-time agent orchestration view</p>
        </div>
        <div className="flex items-center gap-4 text-xs">
          <div className="flex items-center gap-1.5">
            <div className="h-2 w-2 rounded-full bg-accent" />
            <span className="text-muted-foreground">{completedNodes} complete</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="h-2 w-2 rounded-full bg-primary animate-pulse" />
            <span className="text-muted-foreground">{nodes.length - completedNodes} running</span>
          </div>
        </div>
      </div>

      <Tabs value={selectedTab} onValueChange={setSelectedTab} className="flex-1 flex flex-col min-h-0">
        <div className="border-b border-border px-6">
          <TabsList className="h-12 bg-transparent p-0 gap-4">
            <TabsTrigger
              value="graph"
              className="gap-2 data-[state=active]:bg-transparent data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none px-2 pb-3"
            >
              <GitBranch className="h-4 w-4" />
              Graph View
            </TabsTrigger>
            <TabsTrigger
              value="list"
              className="gap-2 data-[state=active]:bg-transparent data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none px-2 pb-3"
            >
              <List className="h-4 w-4" />
              Node List
            </TabsTrigger>
            <TabsTrigger
              value="metrics"
              className="gap-2 data-[state=active]:bg-transparent data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none px-2 pb-3"
            >
              <BarChart3 className="h-4 w-4" />
              Metrics
            </TabsTrigger>
          </TabsList>
        </div>

        <TabsContent value="graph" className="relative flex-1 m-0 p-0 flex-col min-h-0 data-[state=active]:flex">
          <div className="absolute inset-0 overflow-y-auto p-6">
            <MermaidGraph nodes={nodes} activeNodeId={activeNodeId} />
          </div>
        </TabsContent>

        <TabsContent value="list" className="relative flex-1 m-0 p-0 flex-col min-h-0 data-[state=active]:flex">
          <div className="absolute inset-0 overflow-y-auto p-6">
            <AgentNodeList nodes={nodes} activeNodeId={activeNodeId} />
          </div>
        </TabsContent>

        <TabsContent value="metrics" className="relative flex-1 m-0 p-0 flex-col min-h-0 data-[state=active]:flex">
          <div className="absolute inset-0 overflow-y-auto p-6">
            <MetricsPanel totalTokens={totalTokens} totalTime={totalTime} nodes={nodes} metrics={metrics} />
          </div>
        </TabsContent>
      </Tabs>

      {/* Summary footer */}
      <div className="border-t border-border p-4">
        <div className="grid grid-cols-3 gap-4">
          <div className="rounded-lg bg-secondary/50 p-3 text-center">
            <p className="text-lg font-semibold text-foreground">{nodes.length}</p>
            <p className="text-xs text-muted-foreground">Total Agents</p>
          </div>
          <div className="rounded-lg bg-secondary/50 p-3 text-center">
            <p className="text-lg font-semibold text-primary">{totalTokens.toLocaleString()}</p>
            <p className="text-xs text-muted-foreground">Tokens Used</p>
          </div>
          <div className="rounded-lg bg-secondary/50 p-3 text-center">
            <p className="text-lg font-semibold text-accent">{(totalTime / 1000).toFixed(1)}s</p>
            <p className="text-xs text-muted-foreground">Total Time</p>
          </div>
        </div>
      </div>
    </div>
  )
}
