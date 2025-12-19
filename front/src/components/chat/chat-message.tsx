"use client";

import { cn } from "../../lib/utils.ts";
import { Avatar, AvatarFallback } from "../ui/avatar.tsx";
import { Bot, User } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { Message } from "../../lib/types.ts";

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={cn(
        "flex gap-4 animate-in fade-in-0 slide-in-from-bottom-2 duration-300",
        isUser && "flex-row-reverse",
      )}
    >
      <Avatar
        className={cn(
          "h-9 w-9 shrink-0",
          isUser ? "bg-secondary" : "bg-primary/20",
        )}
      >
        <AvatarFallback
          className={cn(
            isUser
              ? "bg-secondary text-secondary-foreground"
              : "bg-primary/20 text-primary",
          )}
        >
          {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
        </AvatarFallback>
      </Avatar>

      <div
        className={cn("flex max-w-[80%] flex-col gap-2", isUser && "items-end")}
      >
        <div
          className={cn(
            "rounded-2xl px-4 py-3",
            isUser
              ? "bg-primary text-primary-foreground rounded-tr-sm"
              : "bg-card border border-border rounded-tl-sm",
          )}
        >
          {message.image && (
            <div className="mb-3 overflow-hidden rounded-lg">
              <img
                src={message.image || "/placeholder.svg"}
                alt="Uploaded medical image"
                className="w-full max-w-[300px] object-cover"
              />
            </div>
          )}
          {isUser
            ? (
              <p className="text-sm leading-relaxed whitespace-pre-wrap">
                {message.content}
              </p>
            )
            : (
              <div className="text-sm leading-relaxed prose prose-sm dark:prose-invert max-w-none break-words prose-p:leading-relaxed prose-pre:bg-secondary/50 prose-pre:p-0">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {message.content}
                </ReactMarkdown>
              </div>
            )}
        </div>

        {message.timestamp && (
          <span className="text-xs text-muted-foreground">
            {message.timestamp}
          </span>
        )}
      </div>
    </div>
  );
}
