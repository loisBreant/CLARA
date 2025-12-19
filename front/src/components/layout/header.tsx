"use client";

import { Activity } from "lucide-react";

export function Header() {
  return (
    <header className="flex h-16 items-center justify-between border-b border-border bg-card px-6">
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/20">
          <Activity className="h-5 w-5 text-primary" />
        </div>
        <div>
          <h1 className="text-lg font-semibold text-foreground">
            MedVision AI
          </h1>
          <p className="text-xs text-muted-foreground">
            Agentic Medical Image Analysis
          </p>
        </div>
      </div>
    </header>
  );
}
