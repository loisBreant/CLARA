"use client";

import { Avatar, AvatarFallback } from "../ui/avatar.tsx";
import { Bot } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface StreamingMessageProps {
  text: string;
}

export function StreamingMessage({ text }: StreamingMessageProps) {
  return (
    <div className="flex gap-4 animate-in fade-in-0 duration-300">
      <Avatar className="h-9 w-9 shrink-0 bg-primary/20">
        <AvatarFallback className="bg-primary/20 text-primary">
          <Bot className="h-4 w-4" />
        </AvatarFallback>
      </Avatar>

      <div className="flex max-w-[80%] flex-col gap-2">
        <div className="rounded-2xl rounded-tl-sm bg-card border border-border px-4 py-3">
          <div className="text-sm leading-relaxed prose prose-sm dark:prose-invert max-w-none break-words [&>*:first-child]:mt-0 [&>*:last-child]:mb-0">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{text}</ReactMarkdown>
            <span className="typing-cursor ml-0.5 inline-block h-4 w-0.5 bg-primary" />
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="h-1.5 w-1.5 rounded-full bg-accent animate-pulse" />
          <span className="text-xs text-muted-foreground">
            AI is responding...
          </span>
        </div>
      </div>
    </div>
  );
}
