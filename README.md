# C.L.A.R.A. (Clinical Logic & Agentic Reasoning Assistant)

CLARA is a project designed to assist with medical image analysis through an AI-powered chat interface. It leverages a multi-agent system to process medical data and provide insights, with a focus on clear and interpretable reasoning.

## Demo

[![Watch the demo video](https://img.youtube.com/vi/YOUR_VIDEO_ID/hqdefault.jpg)](https://www.youtube.com/watch?v=YOUR_VIDEO_ID)
*TODO*

## Getting Started

### Required Api Key
Create a free api key on [openrouter](https://openrouter.ai/settings/keys).
```bash
# Copy the example env file and put your open router api key
cp ./back/.env.example ./back/.env
```

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
-   **Executor Agent:** Executes specific tasks defined by the Planner.
-   **Oncology Agent:** Specializes in analyzing oncology-related medical data.
-   **Summary Agent:** Synthesizes findings into concise summaries.

## TODO

- [x] Agent memory
- [x] Connect agents
- [x] Agents' metrics
- [x] Agents' graph
- [x] Show planners high level steps
- [ ] Save previous messages
- [ ] Send image to backend
- [ ] Segment image
- [ ] Critic agent
