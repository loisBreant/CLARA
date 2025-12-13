"use client";

import type React from "react";

import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send, ImagePlus, Mic } from "lucide-react";
import { ChatMessage } from "./chat-message";
import { StreamingMessage } from "./streaming-message";
import { ImageUploadPreview } from "./image-upload-preview";
import type { Message } from "@/lib/types";

interface ChatPanelProps {
    messages: Message[];
    isStreaming: boolean;
    currentStreamingText: string;
    onSendMessage: (text: string) => void;
    sessionId: string | null; // Add sessionId prop
}

export function ChatPanel({
    messages,
    isStreaming,
    currentStreamingText,
    onSendMessage,
    sessionId,
}: ChatPanelProps) {
    const [input, setInput] = useState("");
    const fileInputRef = useRef<HTMLInputElement>(null);
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages, currentStreamingText]);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (input.trim()) {
            onSendMessage(input);
            setInput("");
        }
    };

    console.log(currentStreamingText);
    const handleImageUploadClick = () => {
        fileInputRef.current?.click();
    };

    const isInputDisabled = isStreaming || !sessionId;

    return (
        <div className="flex flex-1 min-w-0 min-h-0 flex-col border-b md:border-b-0 md:border-r border-border bg-background">
            <div className="flex items-center justify-between border-b border-border px-6 py-4">
                <div>
                    <h2 className="text-sm font-semibold text-foreground">
                        Chat Interface
                    </h2>
                    <p className="text-xs text-muted-foreground">
                        Upload medical images for AI analysis
                    </p>
                </div>
                <div className="flex items-center gap-2">
                    <div className="h-2 w-2 rounded-full bg-accent animate-pulse" />
                    <span className="text-xs text-muted-foreground">Connected</span>
                </div>
            </div>

            <div className="flex-1 overflow-y-auto p-6" ref={scrollRef}>
                <div className="space-y-6">
                    {messages.length === 0 && !isStreaming && (
                        <div className="flex flex-col items-center justify-center py-16 text-center">
                            <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10">
                                <ImagePlus className="h-8 w-8 text-primary" />
                            </div>
                            <h3 className="mb-2 text-lg font-medium text-foreground">
                                Start Medical Image Analysis
                            </h3>
                            <p className="max-w-sm text-sm text-muted-foreground">
                                Upload a medical image (X-ray, CT, MRI) and ask questions about
                                it. Click the demo button to see the AI in action.
                            </p>
                            <Button
                                className="mt-6"
                                onClick={() => onSendMessage("")}
                                disabled={isInputDisabled}
                            >
                                Run Demo Conversation
                            </Button>
                        </div>
                    )}

                    {messages.map((message, index) => (
                        <ChatMessage key={index} message={message} />
                    ))}

                    {isStreaming && currentStreamingText && (
                        <StreamingMessage text={currentStreamingText} />
                    )}
                </div>
            </div>

            <div className="border-t border-border p-4">
                <form onSubmit={handleSubmit} className="flex items-center gap-3">
                    <Input
                        type="file"
                        ref={fileInputRef}
                        className="hidden"
                        accept="image/*"
                    />
                    <Button
                        type="button"
                        variant="outline"
                        size="icon"
                        onClick={handleImageUploadClick}
                        className="shrink-0 bg-transparent"
                        disabled={isInputDisabled}
                    >
                        <ImagePlus className="h-4 w-4" />
                    </Button>

                    <div className="relative flex-1">
                        <Input
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder={
                                isInputDisabled
                                    ? "Initializing chat..."
                                    : "Ask about the medical image..."
                            }
                            className="pr-10 bg-secondary border-0"
                            disabled={isInputDisabled}
                        />
                        <Button
                            type="button"
                            variant="ghost"
                            size="icon"
                            className="absolute right-1 top-1/2 -translate-y-1/2 h-7 w-7"
                            disabled={isInputDisabled}
                        >
                            <Mic className="h-4 w-4 text-muted-foreground" />
                        </Button>
                    </div>

                    <Button
                        type="submit"
                        size="icon"
                        disabled={isInputDisabled}
                        className="shrink-0 bg-primary hover:bg-primary/90"
                    >
                        <Send className="h-4 w-4" />
                    </Button>
                </form>
            </div>
        </div>
    );
}
