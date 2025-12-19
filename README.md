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
