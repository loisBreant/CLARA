"use client";

import { useState, useEffect } from "react";
import { fetchApi } from "@/lib/api";
import { ChatPanel } from "./chat/chat-panel";
import { AgentGraphPanel } from "./agent-graph/agent-graph-panel";
import { Header } from "./layout/header";
import type { Message, AgentNode } from "@/lib/types";

export function MedicalAIChat() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [agentNodes, setAgentNodes] = useState<AgentNode[]>([]);
    const [isStreaming, setIsStreaming] = useState(false);
    const [currentStreamingText, setCurrentStreamingText] = useState("");
    const [activeNodeId, setActiveNodeId] = useState<string | null>(null);
    const [conversationIndex, setConversationIndex] = useState(0); // Keep for demo if needed, otherwise remove
    const [sessionId, setSessionId] = useState<string | null>(null);

    // Initialize session on component mount
    useEffect(() => {
        const initSession = async () => {
            console.log("Attempting to initialize session...");
            try {
                const response = await fetchApi("/init-session", "POST");
                const data = await response.json(); // Explicitly parse JSON here
                setSessionId(data.session_id);
                console.log("Session initialized with ID:", data.session_id);
            } catch (error) {
                console.error("Failed to initialize session:", error);
            }
        };
        initSession();
    }, []);

    const handleSendMessage = async (text: string) => {
        console.log("handleSendMessage called. Current sessionId:", sessionId);
        if (!sessionId) {
            console.error("No session ID available. Message not sent.");
            return;
        }

        const userMessage: Message = { role: "user", content: text };
        setMessages((prev) => [...prev, userMessage]);
        setIsStreaming(true);
        setCurrentStreamingText("");

        try {
            // Assuming the backend /chat endpoint returns a plain text stream
            // We will accumulate the text and then add it as a complete message
            const response = await fetchApi("/chat", "POST", {
                question: text,
                session_id: sessionId,
            });

            const reader = response.body?.getReader();
            if (!reader) {
                throw new Error("Failed to get reader from response body.");
            }

            const decoder = new TextDecoder("utf-8");
            let receivedText = "";

            // Loop to read the stream
            while (true) {
                const { done, value } = await reader.read();
                if (done) {
                    break;
                }
                const chunk = decoder.decode(value, { stream: true });
                setCurrentStreamingText((prev) => prev + chunk);
            }

            // Once the stream is done, move the accumulated text to messages
            const aiMessage: Message = { role: "assistant", content: receivedText };
            setMessages((prev) => [...prev, aiMessage]);
        } catch (error) {
            console.error("Failed to send message:", error);
            // Optionally add an error message to the chat
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

    const handleReset = () => {
        setMessages([]);
        setAgentNodes([]);
        setConversationIndex(0);
        setIsStreaming(false);
        setCurrentStreamingText("");
        setActiveNodeId(null);
        setSessionId(null); // Reset session ID on reset
        // Re-initialize session after reset
        const initSession = async () => {
            try {
                const response = await fetchApi("/init-session", "POST");
                const data = await response.json(); // Explicitly parse JSON here
                setSessionId(data.session_id);
                console.log("Session re-initialized with ID:", data.session_id);
            } catch (error) {
                console.error("Failed to re-initialize session:", error);
            }
        };
        initSession();
    };

    return (
        <div className="flex h-screen flex-col bg-background">
            <Header onReset={handleReset} />
            <div className="flex flex-1 min-h-0 flex-col md:flex-row overflow-hidden">
                <ChatPanel
                    messages={messages}
                    isStreaming={isStreaming}
                    currentStreamingText={currentStreamingText}
                    onSendMessage={handleSendMessage}
                    sessionId={sessionId}
                />
                <AgentGraphPanel nodes={agentNodes} activeNodeId={activeNodeId} />
            </div>
        </div>
    );
}
