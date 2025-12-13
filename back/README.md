### Run the backend in dev mode

1. Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Run backend

```bash
uv run fastapi dev src/main.py
```

### Format / type-check the project

```bash
ruff check --fix
```

```bash
ruff format
```

```bash
ty check
```
