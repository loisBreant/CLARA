1. Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

This project C.L.A.R.A. stands for Clinical Logic & Agentic Reasoning Assistant.

1. Run back and front

```bash
docker compose up --build
```

1.  Go on `http://localhost:8501` to view the front

Agent:
- 1. Planneur agent
- 1. Executor agent
- 1. Oncology agent
- 1. Summary agent

TODO:
- [ ] Save previous messages
- [ ] Agent memory
- [ ] Connect agents
- [ ] Agents' metrics
- [ ] Agents' graph
- [ ] Show planners high level steps
