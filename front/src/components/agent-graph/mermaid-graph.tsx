"use client";

import { useEffect, useRef, useState } from "react";
import mermaid from "mermaid";
import { cn } from "@/lib/utils";
import type { AgentNode } from "@/lib/types";

interface MermaidGraphProps {
    nodes: AgentNode[];
    activeNodeId: string | null;
}

export function MermaidGraph({ nodes, activeNodeId }: MermaidGraphProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    const [rendered, setRendered] = useState(false);

    useEffect(() => {
        mermaid.initialize({
            startOnLoad: false,
            theme: "dark",
            securityLevel: "loose", // Allow HTML in labels
            htmlLabels: true, // Render labels as HTML
            themeVariables: {
                primaryColor: "#6366f1",
                primaryTextColor: "#f1f5f9",
                primaryBorderColor: "#4f46e5",
                lineColor: "#475569",
                secondaryColor: "#1e293b",
                tertiaryColor: "#0f172a",
            },
            flowchart: {
                curve: "basis",
                padding: 20,
                nodeSpacing: 50,
                rankSpacing: 60,
            },
        });
    }, []);

    useEffect(() => {
        const renderGraph = async () => {
            if (!containerRef.current || nodes.length === 0) return;

            const graphDefinition = generateMermaidDefinition(nodes, activeNodeId);

            try {
                containerRef.current.innerHTML = "";
                const graphId = `agent-graph-${Date.now()}`;
                const { svg } = await mermaid.render(graphId, graphDefinition);
                containerRef.current.innerHTML = svg;
                setRendered(true);
            } catch (error) {
                console.error("Mermaid rendering error:", error);
            }
        };

        renderGraph();
    }, [nodes, activeNodeId]);

    if (nodes.length === 0) {
        return (
            <div className="flex h-64 items-center justify-center text-center">
                <div>
                    <div className="mb-3 mx-auto h-12 w-12 rounded-full bg-secondary flex items-center justify-center">
                        <span className="text-2xl">🔗</span>
                    </div>
                    <p className="text-sm text-muted-foreground">
                        Agent workflow will appear here during analysis
                    </p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            <div
                ref={containerRef}
                className={cn(
                    "mermaid-container rounded-lg bg-secondary/30 p-4 overflow-x-auto",
                    "transition-opacity duration-300",
                    rendered ? "opacity-100" : "opacity-0",
                )}
            />

            {/* Legend */}
            <div className="flex items-center justify-center gap-6 text-xs">
                <div className="flex items-center gap-2">
                    <div className="h-3 w-3 rounded bg-primary" />
                    <span className="text-muted-foreground">Active</span>
                </div>
                <div className="flex items-center gap-2">
                    <div className="h-3 w-3 rounded bg-accent" />
                    <span className="text-muted-foreground">Complete</span>
                </div>
                <div className="flex items-center gap-2">
                    <div className="h-3 w-3 rounded bg-secondary" />
                    <span className="text-muted-foreground">Pending</span>
                </div>
            </div>
        </div>
    );
}

// - Using quoted strings for labels to handle special characters
// - Removed HTML tags that cause parsing issues
// - Using proper node shape syntax
function generateMermaidDefinition(
    nodes: AgentNode[],
    activeNodeId: string | null,
): string {
    const lines: string[] = ["flowchart TD"];

    // Add styling classes
    lines.push(
        "  classDef active fill:#6366f1,stroke:#4f46e5,stroke-width:2px,color:#fff,font-weight:bold",
    );
    lines.push(
        "  classDef complete fill:#22c55e,stroke:#16a34a,stroke-width:2px,color:#fff",
    );
    lines.push(
        "  classDef pending fill:#334155,stroke:#475569,stroke-width:1px,color:#94a3b8",
    );
    lines.push("");

    const emojiMap: Record<string, string> = {
      // Orchestrator: '🧠',
      // Vision: '👁️',
      // Analysis: '🔬',
      // Response: '💬',
      // Diagnosis: '🩺',
    };

    // Add nodes with properly escaped labels
    nodes.forEach((node) => {
      // const icon = emojiMap[node.type] || '⚙️'; // Default icon
      const htmlLabel = `<div style="padding: 8px; text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #f1f5f9;"><span style="font-weight: 600; font-size: 1.1em; margin-top: 4px;">${node.name}</span><span style="font-size: 0.8em; opacity: 0.8; margin-top: 2px;">${node.tokens}tok &bull; ${node.duration}ms</span></div>`;

      // Mermaid requires HTML labels to be wrapped in "%%" for explicit HTML,
      // or to use a specific syntax for different node types if htmlLabels is true.
      // We're using the standard shape syntax which accepts HTML content when htmlLabels is true.
      if (node.type === "orchestrator") {
        lines.push(`  ${node.id}{${htmlLabel}}`) // Diamond shape
      } else {
        lines.push(`  ${node.id}[${htmlLabel}]`) // Default rounded rect
      }
    });

    lines.push("");

    // Add connections
    const edges = new Set<string>();
    const addEdge = (from: string, to: string) => {
        if (!edges.has(`${from}-${to}`)) {
            lines.push(`  ${from} --> ${to}`);
            edges.add(`${from}-${to}`);
        }
    };

    nodes.forEach((node) => {
        if (node.parentId) {
            const parent = nodes.find((n) => n.id === node.parentId);
            if (parent) {
                addEdge(node.parentId, node.id);
            }
        }

        if (node.childrenIds && node.childrenIds.length > 0) {
            node.childrenIds.forEach((childId) => {
                const child = nodes.find((n) => n.id === childId);
                if (child) {
                    addEdge(node.id, childId);
                }
            });
        }
    });

    lines.push("");

    // Apply classes
    nodes.forEach((node) => {
        if (node.id === activeNodeId) {
            lines.push(`  class ${node.id} active`);
        } else if (node.status === "complete") {
            lines.push(`  class ${node.id} complete`);
        } else {
            lines.push(`  class ${node.id} pending`);
        }
    });

    return lines.join("\n");
}
