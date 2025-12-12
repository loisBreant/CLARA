# MedVision AI (CLARA Frontend)

This project is the frontend interface for MedVision AI (CLARA), a medical image analysis chat application. It allows users to upload medical images (X-ray, CT, MRI) and interact with an AI agent to analyze them. The application visualizes the agent's reasoning process via a dynamic graph.

**Note:** This project has been migrated from Next.js to **Vite + React** and utilizes **Deno** for development and build workflows.

## Tech Stack

- **Framework:** React 19 (Vite)
- **Runtime & Tooling:** Deno v2
- **Language:** TypeScript
- **Styling:** Tailwind CSS v4, CSS Modules
- **UI Components:** Shadcn UI (Radix Primitives + Tailwind)
- **Visualization:** Recharts (Charts), Mermaid (Agent Graph)
- **Icons:** Lucide React

## Project Structure

```
/
├── deno.json           # Deno configuration and task definitions
├── package.json        # NPM dependencies (managed by Deno)
├── vite.config.ts      # Vite configuration
├── Dockerfile          # Deno-based Docker build
├── src/
│   ├── main.tsx        # Application entry point
│   ├── App.tsx         # Root component
│   ├── index.css       # Global styles (Tailwind imports)
│   ├── components/     # React components
│   │   ├── agent-graph/# Components for visualizing the AI agent workflow
│   │   ├── chat/       # Chat interface components
│   │   ├── layout/     # Header and layout components
│   │   ├── ui/         # Reusable UI components (buttons, inputs, etc.)
│   │   └── medical-ai-chat.tsx # Main feature container
│   ├── lib/            # Utilities and mock data
│   └── hooks/          # Custom React hooks
```

## Getting Started

### Prerequisites

- **Deno:** Ensure you have Deno installed (v2 recommended).

### Installation

Dependencies are installed automatically by Deno when running tasks, but you can explicitly cache them:

```bash
deno install
```

### Development

Start the Vite development server:

```bash
deno task dev
```

The application will be available at `http://localhost:5173`.

### Building for Production

Build the application to the `dist` directory:

```bash
deno task build
```

Preview the production build locally:

```bash
deno task preview
```

### Docker

The project includes a multi-stage Dockerfile that uses `denoland/deno:alpine`.

**Build the image:**

```bash
docker build -t medvision-ai .
```

**Run the container:**

```bash
docker run -p 3000:3000 medvision-ai
```

(The container serves the static `dist` folder on port 3000).

## Development Conventions

- **Deno-First:** We use `deno task` for all lifecycle scripts. Avoid using `npm` or `yarn` directly.
- **Imports:** Path alias `@/*` is configured to resolve to `./src/*`.
- **Styling:** Use Tailwind utility classes. Global themes and variables are defined in `src/index.css`.
- **Icons:** Use `lucide-react` components.
- **Fonts:** "Plus Jakarta Sans" for UI, "JetBrains Mono" for code. configured via `src/index.css` and `index.html`.

## Key Features

1.  **Medical AI Chat:** Interactive chat interface for discussing medical images.
2.  **Agent Graph:** Real-time visualization of the AI's internal thought process and "agents" (nodes).
3.  **Mock Data:** currently driven by `src/lib/mock-data.ts` for demonstration purposes.
