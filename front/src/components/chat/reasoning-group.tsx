"use client"

import { cn } from "@/lib/utils"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Bot, Brain, ChevronDown } from "lucide-react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import type { Message } from "@/lib/types"
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible"

interface ReasoningGroupProps {
  messages: Message[]
}

export function ReasoningGroup({ messages }: ReasoningGroupProps) {
  if (messages.length === 0) return null

  // Use the timestamp of the first message, or none
  const timestamp = messages[0].timestamp

  return (
    <div className="flex gap-4 animate-in fade-in-0 slide-in-from-bottom-2 duration-300">
      <Avatar className="h-9 w-9 shrink-0 bg-primary/20">
        <AvatarFallback className="bg-primary/20 text-primary">
          <Bot className="h-4 w-4" />
        </AvatarFallback>
      </Avatar>

      <div className="flex max-w-[80%] flex-col gap-2 w-full">
        <div className="rounded-2xl px-4 py-3 bg-muted/30 border border-border/50 rounded-tl-sm w-full">
          <Collapsible>
            <CollapsibleTrigger className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors w-full text-left group">
              <Brain className="h-4 w-4" />
              <span className="font-medium">
                Thinking Process ({messages.length} step{messages.length > 1 ? "s" : ""})
              </span>
              <ChevronDown className="h-4 w-4 ml-auto transition-transform group-data-[state=open]:rotate-180" />
            </CollapsibleTrigger>
            
            <CollapsibleContent>
              <div className="mt-3 space-y-3 border-t border-border/50 pt-3">
                {messages.map((msg, idx) => (
                  <Collapsible key={idx} className="pl-2 border-l-2 border-border/50">
                    <CollapsibleTrigger className="flex items-center gap-2 text-xs text-muted-foreground hover:text-foreground transition-colors w-full text-left group py-1">
                       <span className="uppercase font-semibold tracking-wider opacity-70">
                        {msg.agentType === "planner" ? "Planning" : "Execution"}
                      </span>
                      <ChevronDown className="h-3 w-3 ml-auto transition-transform group-data-[state=open]:rotate-180 opacity-50" />
                    </CollapsibleTrigger>
                    <CollapsibleContent>
                         <div className="mt-1 text-sm leading-relaxed prose prose-sm dark:prose-invert max-w-none break-words prose-p:leading-relaxed prose-pre:bg-secondary/50 prose-pre:p-0 text-muted-foreground/90">
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
                        </div>
                    </CollapsibleContent>
                  </Collapsible>
                ))}
              </div>
            </CollapsibleContent>
          </Collapsible>
        </div>
        {timestamp && <span className="text-xs text-muted-foreground">{timestamp}</span>}
      </div>
    </div>
  )
}
