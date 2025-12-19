# C.L.A.R.A. (Clinical Logic & Agentic Reasoning Assistant)

CLARA is a project designed to assist with medical image analysis through an AI-powered chat interface. It leverages a multi-agent system to process medical data and provide insights, with a focus on clear and interpretable reasoning.

## Demo

https://github.com/user-attachments/assets/f90fe625-6b4e-4a7f-979c-d0f4243d848c



## Getting Started

### Required Api Key
Create a free api key on [openrouter](https://openrouter.ai/settings/keys).
```bash
# Copy the example env file and put your open router api key
cp ./back/.env.example ./back/.env
```

## Documentation
- [Project Report](report.pdf)
The source code of the report can be found at `./report`.

### Development

For development instructions, please refer to the specific `README.md` files located in the `back/` and `front/` directories.

### Production Deployment

To run the entire CLARA application in a production-like environment using Docker:

1.  Build and start the services:
    ```bash
    docker compose up --build
    ```
2.  Access the frontend application in your browser at `http://localhost:8080`.

## Core AI Agents

CLARA's intelligence is powered by a collaborative system of specialized AI agents:

-   **Planner Agent:** Orchestrates the overall analysis process.
-   **Executor Agent:** Executes specific tasks defined by the Planner. (uses Vision agent)
-   **Oncology Agent:** Specializes in analyzing oncology-related medical data.
-   **Summary Agent:** Synthesizes findings into concise summaries.

## Project tree
```bash
.
├── README.md             # <--- You are here :)
├── demo/                 # Demo related scripts and configurations
├── docker-compose.yml    # Docker Compose configuration for the entire application
├── flake.nix             # Nix flake configuration
├── back/                 # Backend service
│   ├── data/             # Database and persistent storage for the backend
│   ├── Dockerfile        # Dockerfile for the backend service
│   ├── pyproject.toml    # Python project dependencies and metadata
│   ├── README.md         # Backend specific README
│   ├── src/              # Backend source code
│   │   ├── agents/       # AI agent implementations
│   │   ├── core/         # Core backend functionalities and models
│   │   ├── main.py       # Main backend application entry point
│   │   └── tools/        # Tools used by AI agents
│   └── telemetrics.csv   # Telemetry/metrics data for agent usage
├── front/                # Frontend application (Vite, React, TypeScript)
│   ├── Dockerfile        # Dockerfile for the frontend service
│   ├── index.html        # Frontend entry HTML file
│   ├── package.json      # Frontend NPM dependencies
│   ├── public/           # Static assets for the frontend
│   ├── README.md         # Frontend specific README
│   ├── src/              # Frontend source code
│   │   ├── App.tsx       # Main React application component
│   │   ├── components/   # Reusable React components
│   │   ├── hooks/        # Custom React hooks
│   │   ├── lib/          # Frontend utilities and mock data
│   │   └── main.tsx      # Frontend entry point
│   └── styles/           # Frontend global styles
└── report/               # Project report and related files
    ├── images/           # Images used in the report
    ├── main.typ          # Source file for the project report
    └── scripts/          # Scripts for generating report assets
```

## TODO

- [x] Agent memory
- [x] Connect agents
- [x] Agents' metrics
- [x] Agents' graph
- [x] Show planners high level steps
- [x] Send image to backend
- [ ] Save previous messages
- [ ] Segment image
- [ ] Critic agent
