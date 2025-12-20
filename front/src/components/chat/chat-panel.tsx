"use client";

import type React from "react";

import { useEffect, useMemo, useRef, useState } from "react";
import { Button } from "../ui/button.tsx";
import { Input } from "../ui/input.tsx";
import { ImagePlus, Mic, Send, X } from "lucide-react";
import { ChatMessage } from "./chat-message.tsx";
import { StreamingMessage } from "./streaming-message.tsx";
import { ReasoningGroup } from "./reasoning-group.tsx";
import type { Message } from "../../lib/types.ts";

interface ChatPanelProps {
  messages: Message[];
  isStreaming: boolean;
  currentStreamingText: string;
  onSendMessage: (text: string, file?: File) => void;
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
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  const [isRecording, setIsRecording] = useState(false);
  const [recognitionError, setRecognitionError] = useState<string | null>(null);
  const speechRecognitionRef = useRef<SpeechRecognition | null>(null);

  useEffect(() => {
    if ("SpeechRecognition" in window || "webkitSpeechRecognition" in window) {
      const SpeechRecognition = globalThis.SpeechRecognition ||
        globalThis.webkitSpeechRecognition;
      speechRecognitionRef.current = new SpeechRecognition();
      speechRecognitionRef.current.continuous = false;
      speechRecognitionRef.current.interimResults = false;
      speechRecognitionRef.current.lang = "fr-FR";

      speechRecognitionRef.current.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setInput((prevInput) => prevInput + transcript);
        setIsRecording(false);
        setRecognitionError(null); // Clear error on successful result
      };

      speechRecognitionRef.current.onerror = (event) => {
        console.error("Speech recognition error:", event.error);
        setIsRecording(false);
        setRecognitionError(
          `Erreur de reconnaissance vocale: ${event.error}. Veuillez réessayer.`,
        );
      };

      speechRecognitionRef.current.onend = () => {
        setIsRecording(false);
      };
    } else {
      console.warn("Speech Recognition API not supported in this browser.");
    }

    return () => {
      if (speechRecognitionRef.current) {
        speechRecognitionRef.current.stop();
      }
    };
  }, []); // Empty dependency array to run once on mount

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, currentStreamingText]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() || selectedFile) {
      onSendMessage(input, selectedFile || undefined);
      setInput("");
      setSelectedFile(null);
      setRecognitionError(null); // Clear error on send
    }
  };

  const handleImageUploadClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
      fileInputRef.current.click();
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const toggleRecording = () => {
    if (!speechRecognitionRef.current) return;

    if (isRecording) {
      speechRecognitionRef.current.stop();
      setIsRecording(false);
    } else {
      setInput(""); // Clear input before starting new speech input
      setRecognitionError(null); // Clear previous errors
      speechRecognitionRef.current.start();
      setIsRecording(true);
    }
  };

  const isInputDisabled = isStreaming || !sessionId;

  // Group consecutive reasoning messages
  const groupedMessages = useMemo(() => {
    const groups: (Message | Message[])[] = [];
    let currentReasoningGroup: Message[] = [];

    messages.forEach((msg) => {
      const isReasoning = !msg.role ||
        (msg.role === "assistant" && msg.agentType &&
          msg.agentType !== "reactive");

      if (isReasoning) {
        currentReasoningGroup.push(msg);
      } else {
        if (currentReasoningGroup.length > 0) {
          groups.push([...currentReasoningGroup]);
          currentReasoningGroup = [];
        }
        groups.push(msg);
      }
    });

    if (currentReasoningGroup.length > 0) {
      groups.push([...currentReasoningGroup]);
    }

    return groups;
  }, [messages]);

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
              <p className="max-w-lm text-sm text-muted-foreground">
                Upload a medical image (X-ray, CT, MRI) and ask questions about
                it.
              </p>
            </div>
          )}

          {groupedMessages.map((group, index) => {
            if (Array.isArray(group)) {
              return <ReasoningGroup key={index} messages={group} />;
            } else {
              return <ChatMessage key={index} message={group} />;
            }
          })}

          {isStreaming && currentStreamingText && (
            <StreamingMessage text={currentStreamingText} />
          )}
        </div>
      </div>

      <div className="border-t border-border p-4">
        {selectedFile && (
          <div className="mb-2 flex items-center gap-2 rounded-md border border-border bg-secondary/50 p-2 text-sm">
            <span className="truncate max-w-[200px]">{selectedFile.name}</span>
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="h-5 w-5 hover:bg-destructive/10 hover:text-destructive"
              onClick={handleRemoveFile}
            >
              <X className="h-3 w-3" />
            </Button>
          </div>
        )}
        {recognitionError && (
          <div className="text-red-500 text-sm mb-2">{recognitionError}</div>
        )}
        <form onSubmit={handleSubmit} className="flex items-center gap-3">
          <Input
            type="file"
            ref={fileInputRef}
            className="hidden"
            accept="image/*"
            onChange={handleFileChange}
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
              placeholder={isInputDisabled
                ? "Initializing chat..."
                : "Ask about the medical image..."}
              className="pr-10 bg-secondary border-0"
              disabled={isInputDisabled}
            />
            {"SpeechRecognition" in window ||
                "webkitSpeechRecognition" in window
              ? (
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className={`absolute right-1 top-1/2 -translate-y-1/2 h-7 w-7 ${
                    isRecording ? "animate-pulse text-red-500" : ""
                  }`}
                  onClick={toggleRecording}
                  disabled={isInputDisabled}
                >
                  <Mic className="h-4 w-4" />
                </Button>
              )
              : null}
          </div>

          <Button
            type="submit"
            size="icon"
            disabled={isInputDisabled || (!input.trim() && !selectedFile)}
            className="shrink-0 bg-primary hover:bg-primary/90"
          >
            <Send className="h-4 w-4" />
          </Button>
        </form>
      </div>
    </div>
  );
}
