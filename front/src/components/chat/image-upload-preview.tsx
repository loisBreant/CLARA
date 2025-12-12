"use client"

import { Button } from "@/components/ui/button"
import { X } from "lucide-react"

interface ImageUploadPreviewProps {
  onRemove: () => void
}

export function ImageUploadPreview({ onRemove }: ImageUploadPreviewProps) {
  return (
    <div className="mb-3 flex items-center gap-3 rounded-lg bg-secondary p-3 animate-in fade-in-0 slide-in-from-bottom-2 duration-200">
      <div className="relative h-16 w-16 overflow-hidden rounded-lg bg-muted">
        <img src="/chest-xray.png" alt="Upload preview" className="h-full w-full object-cover" />
      </div>
      <div className="flex-1">
        <p className="text-sm font-medium text-foreground">chest_xray_001.dcm</p>
        <p className="text-xs text-muted-foreground">Medical Image • 2.4 MB</p>
      </div>
      <Button variant="ghost" size="icon" onClick={onRemove} className="h-8 w-8 shrink-0">
        <X className="h-4 w-4" />
      </Button>
    </div>
  )
}
