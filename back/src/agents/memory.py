from typing import Any, Dict, List


class MemoryAgent:
    def __init__(self):
        self._storage: Dict[str, Any] = {}

    def get(self, key: str) -> Any:
        return self._storage.get(key)

    def set(self, key: str, value: Any):
        self._storage[key] = value

    def resolve(self, arg: Any) -> Any:
        if isinstance(arg, str) and arg.startswith("$"):
            key_to_find = arg[1:] 
            if key_to_find in self._storage:
                return self._storage[key_to_find]

            if arg in self._storage:
                return self._storage[arg]

            raise ValueError(
                f"Variable '{arg}' not found"
            )

        return arg

    def resolve_args(self, args: List[Any]) -> List[Any]:
        return [self.resolve(arg) for arg in args]

    def dump(self) -> Dict[str, Any]:
        return self._storage
