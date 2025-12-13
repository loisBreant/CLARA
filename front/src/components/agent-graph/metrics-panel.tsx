"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts"
import type { AgentNode, AgentMetrics } from "@/lib/types"

interface MetricsPanelProps {
  nodes: AgentNode[]
  metrics: AgentMetrics | null
}

export function MetricsPanel({ nodes, metrics }: MetricsPanelProps) {
  const tokenData = nodes.map((node) => ({
    name: node.name.split(" ")[0],
    tokens: node.tokens,
    time: node.duration,
  }))

  const statusData = [
    { name: "Complete", value: nodes.filter((n) => n.status === "complete").length, color: "#22c55e" },
    { name: "Running", value: nodes.filter((n) => n.status === "running").length, color: "#6366f1" },
    { name: "Pending", value: nodes.filter((n) => n.status === "pending").length, color: "#475569" },
  ].filter((d) => d.value > 0)

  if (nodes.length === 0 && !metrics) {
    return (
      <div className="flex h-64 items-center justify-center text-center">
        <p className="text-sm text-muted-foreground">Metrics will appear once agents start processing</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Overview Cards */}
      <div className="grid grid-cols-2 gap-4">
        <Card className="bg-secondary/30 border-border">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-medium text-muted-foreground">Total Input Tokens</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">
              {metrics?.input_token_count.toLocaleString() || "0"}
            </div>
            <p className="text-xs text-muted-foreground">
              Current Input Tokens: {metrics?.current_input_token_count.toLocaleString() || "0"}
            </p>
            <Progress value={Math.min(((metrics?.input_token_count || 0) / 10000) * 100, 100)} className="mt-3 h-1.5" />
          </CardContent>
        </Card>

        <Card className="bg-secondary/30 border-border">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-medium text-muted-foreground">Total Output Tokens</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">
              {metrics?.output_token_count.toLocaleString() || "0"}
            </div>
            <p className="text-xs text-muted-foreground">
              Time taken for current chunk: {(metrics?.current_time_taken || 0).toFixed(2)}s
            </p>
            <Progress value={Math.min(((metrics?.output_token_count || 0) / 10000) * 100, 100)} className="mt-3 h-1.5" />
          </CardContent>
        </Card>

        <Card className="bg-secondary/30 border-border">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-medium text-muted-foreground">Total Time Taken</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">
              {(metrics?.total_time_taken || 0).toFixed(2)}s
            </div>
            <p className="text-xs text-muted-foreground">overall processing time</p>
            <Progress value={Math.min(((metrics?.total_time_taken || 0) / 60) * 100, 100)} className="mt-3 h-1.5" />
          </CardContent>
        </Card>
      </div>

      {/* Token Distribution Chart */}
      <Card className="bg-secondary/30 border-border">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-foreground">Token Distribution by Agent</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={tokenData} layout="vertical">
                <XAxis type="number" tick={{ fill: "#94a3b8", fontSize: 10 }} />
                <YAxis type="category" dataKey="name" tick={{ fill: "#94a3b8", fontSize: 10 }} width={80} />
                <Tooltip
                  contentStyle={{
                    background: "#1e293b",
                    border: "1px solid #334155",
                    borderRadius: "8px",
                    color: "#f1f5f9",
                  }}
                />
                <Bar dataKey="tokens" fill="#6366f1" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Status Distribution */}
      <Card className="bg-secondary/30 border-border">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-foreground">Agent Status Distribution</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-8">
            <div className="h-32 w-32">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={statusData}
                    cx="50%"
                    cy="50%"
                    innerRadius={30}
                    outerRadius={50}
                    paddingAngle={2}
                    dataKey="value"
                  >
                    {statusData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="space-y-2">
              {statusData.map((item) => (
                <div key={item.name} className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full" style={{ backgroundColor: item.color }} />
                  <span className="text-sm text-muted-foreground">
                    {item.name}: {item.value}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
