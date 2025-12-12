import type { Message, AgentNode } from "./types"

export const mockConversation: Message[] = [
  {
    role: "user",
    content: "Can you analyze this chest X-ray and tell me if there are any abnormalities?",
    image: "/chest-xray-medical-scan.jpg",
    timestamp: "10:32 AM",
  },
  {
    role: "assistant",
    content: `I've analyzed the chest X-ray image you provided. Here's my comprehensive assessment:

**Image Quality Assessment:**
The image quality is good with adequate penetration and proper positioning. The patient appears to be in a standard PA (posteroanterior) view.

**Key Findings:**

1. **Lung Fields:** Both lung fields appear clear with no obvious consolidation, masses, or nodules visible. The lung markings are within normal limits.

2. **Heart Size:** The cardiac silhouette appears within normal limits. The cardiothoracic ratio is approximately 0.45, which is within the normal range (<0.5).

3. **Mediastinum:** The mediastinal contours appear normal. No widening or abnormal masses detected.

4. **Costophrenic Angles:** Both costophrenic angles are sharp, suggesting no pleural effusion.

5. **Bony Structures:** The visible bony structures including ribs, clavicles, and spine appear intact without obvious fractures or lesions.

**Impression:**
This appears to be a **normal chest X-ray** with no significant abnormalities detected. However, I recommend:
- Clinical correlation with patient symptoms
- Follow-up imaging if symptoms persist
- Consultation with a radiologist for definitive interpretation

Would you like me to explain any of these findings in more detail?`,
    timestamp: "10:33 AM",
  },
  {
    role: "user",
    content: "What specific features did you look for when analyzing the lung fields?",
    timestamp: "10:35 AM",
  },
  {
    role: "assistant",
    content: `Great question! When analyzing the lung fields in a chest X-ray, I systematically evaluate several key features:

**1. Density Patterns:**
- **Normal:** Lungs should appear dark/black due to air content
- **Abnormal:** Look for areas of increased density (whiteness) which could indicate:
  - Consolidation (pneumonia)
  - Masses or nodules
  - Atelectasis (lung collapse)

**2. Lung Markings:**
- Normal branching vascular patterns radiating from the hilum
- Should decrease in caliber towards the periphery
- Abnormal markings may suggest:
  - Pulmonary edema (prominence)
  - Emphysema (reduced markings)

**3. Distribution Assessment:**
- Compare both lungs for symmetry
- Divide each lung into zones (upper, middle, lower)
- Look for focal vs. diffuse abnormalities

**4. Specific Pathology Signs:**
- **Air bronchograms:** Air-filled bronchi visible against dense lung tissue
- **Silhouette sign:** Loss of normal borders suggesting adjacent pathology
- **Kerley B lines:** Horizontal lines indicating interstitial edema

**5. Borders & Interfaces:**
- Clear fissure lines
- Sharp diaphragmatic borders
- Normal hilar structures

In your X-ray, all these features appeared within normal limits, which is why I concluded the lung fields are clear.`,
    timestamp: "10:36 AM",
  },
]

export const mockAgentNodes: AgentNode[] = [
  // First response agents
  {
    id: "orch-1",
    name: "Orchestrator Agent",
    type: "orchestrator",
    description: "Coordinates the analysis workflow and determines which specialized agents to invoke",
    status: "pending",
    tokens: 245,
    duration: 180,
    childrenIds: ["vision-1", "vision-2"],
    messageIndex: 1,
  },
  {
    id: "vision-1",
    name: "Vision Processing Agent",
    type: "vision",
    description: "Processes and extracts features from the uploaded medical image using GPT-4V",
    status: "pending",
    tokens: 1850,
    duration: 2400,
    parentId: "orch-1",
    childrenIds: ["diag-1"],
    messageIndex: 1,
  },
  {
    id: "vision-2",
    name: "Vision Verification Agent",
    type: "vision",
    description: "Verifies the findings of the primary vision agent",
    status: "pending",
    tokens: 1200,
    duration: 1500,
    parentId: "orch-1",
    messageIndex: 1,
  },
  {
    id: "diag-1",
    name: "Diagnostic Analysis Agent",
    type: "diagnosis",
    description: "Analyzes extracted features against medical knowledge base for potential findings",
    status: "pending",
    tokens: 1420,
    duration: 1800,
    parentId: "vision-1",
    childrenIds: ["analysis-1"],
    messageIndex: 1,
  },
  {
    id: "analysis-1",
    name: "Report Generation Agent",
    type: "analysis",
    description: "Compiles findings into a structured medical report format",
    status: "pending",
    tokens: 890,
    duration: 950,
    parentId: "diag-1",
    childrenIds: ["response-1"],
    messageIndex: 1,
  },
  {
    id: "response-1",
    name: "Response Synthesis Agent",
    type: "response",
    description: "Formats the final response with appropriate medical terminology and recommendations",
    status: "pending",
    tokens: 620,
    duration: 450,
    parentId: "analysis-1",
    messageIndex: 1,
  },

  // Second response agents
  {
    id: "orch-2",
    name: "Query Understanding Agent",
    type: "orchestrator",
    description: "Interprets the follow-up question and determines response strategy",
    status: "pending",
    tokens: 180,
    duration: 150,
    messageIndex: 3,
  },
  {
    id: "analysis-2",
    name: "Medical Knowledge Agent",
    type: "analysis",
    description: "Retrieves relevant medical knowledge about lung field analysis techniques",
    status: "pending",
    tokens: 1100,
    duration: 1200,
    parentId: "orch-2",
    messageIndex: 3,
  },
  {
    id: "response-2",
    name: "Educational Response Agent",
    type: "response",
    description: "Structures the response in an educational format with clear explanations",
    status: "pending",
    tokens: 780,
    duration: 600,
    parentId: "analysis-2",
    messageIndex: 3,
  },
]
