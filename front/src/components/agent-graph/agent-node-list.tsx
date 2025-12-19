"use client";

import type React from "react";

import { cn } from "../../lib/utils.ts";
import { Badge } from "../ui/badge.tsx";
import {
  Brain,
  Clock,
  Eye,
  FileSearch,
  MessageSquare,
  Stethoscope,
  Zap,
} from "lucide-react";
import type { AgentNode } from "../../lib/types.ts";

interface AgentNodeListProps {
  nodes: AgentNode[];
  activeNodeId: string | null;
}

const iconMap: Record<string, React.ElementType> = {
  orchestrator: Brain,
  vision: Eye,
  analysis: FileSearch,
  response: MessageSquare,
  diagnosis: Stethoscope,
  planner: Brain,
  executor: Stethoscope,
  reactive: Zap,
};

export function AgentNodeList({ nodes, activeNodeId }: AgentNodeListProps) {
  if (nodes.length === 0) {
    return (
      <div className="flex h-64 items-center justify-center text-center">
        <p className="text-sm text-muted-foreground">
          No agents have been invoked yet
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {nodes.map((node, index) => {
        const Icon = iconMap[node.type] || Brain;
        const isActive = node.id === activeNodeId;
        const isComplete = node.status === "complete";

        return (
          <div
            key={node.id}
            className={cn(
              "rounded-lg border p-4 transition-all duration-300",
              "animate-in fade-in-0 slide-in-from-left-2",
              isActive && "border-primary bg-primary/10 pulse-glow",
              isComplete && "border-accent/50 bg-accent/5",
              !isActive && !isComplete && "border-border bg-card",
            )}
            style={{ animationDelay: `${index * 100}ms` }}
          >
            <div className="flex items-start gap-3">
              <div
                className={cn(
                  "flex h-10 w-10 shrink-0 items-center justify-center rounded-lg",
                  isActive && "bg-primary text-primary-foreground",
                  isComplete && "bg-accent text-accent-foreground",
                  !isActive && !isComplete &&
                    "bg-secondary text-muted-foreground",
                )}
              >
                <Icon className="h-5 w-5" />
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <h4 className="font-medium text-sm text-foreground truncate">
                    {node.name}
                  </h4>
                  <Badge
                    variant={isComplete ? "default" : "secondary"}
                    className={cn(
                      "text-xs",
                      isActive && "bg-primary",
                      isComplete && "bg-accent",
                    )}
                  >
                    {isActive ? "Running" : isComplete ? "Complete" : "Pending"}
                  </Badge>
                </div>

                <p className="text-xs text-muted-foreground mb-3 line-clamp-2">
                  {node.description}
                </p>

                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-1.5 text-xs">
                    <Zap className="h-3 w-3 text-chart-3" />
                    <span className="text-muted-foreground">
                      {node.tokens.toLocaleString()} tokens
                    </span>
                  </div>
                  <div className="flex items-center gap-1.5 text-xs">
                    <Clock className="h-3 w-3 text-chart-1" />
                    <span className="text-muted-foreground">
                      {(node.duration / 1000).toFixed(1)}s
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {isActive && (
              <div className="mt-3 h-1 overflow-hidden rounded-full bg-secondary">
                <div
                  className="h-full w-1/2 animate-pulse rounded-full bg-primary"
                  style={{
                    animation: "progress 2s ease-in-out infinite",
                  }}
                />
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
