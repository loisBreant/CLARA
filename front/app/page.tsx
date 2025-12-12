"use client"

import dynamic from 'next/dynamic'

const MedicalAIChat = dynamic(() => import("../components/medical-ai-chat").then(mod => mod.MedicalAIChat), { ssr: false })

export default function Page() {
  return <MedicalAIChat />
}
