from typing import Any, Dict, List

class MemoryAgent:
    def __init__(self):
        self._storage: Dict[str, Any] = {}

    def get(self, key: str) -> Any:
        return self._storage.get(key)

    def set(self, key: str, value: Any):
        self._storage[key] = value

    def resolve(self, arg: Any) -> Any:
        """
        Résout une variable si elle commence par '$'.
        Sinon renvoie la valeur telle quelle.
        """
        if isinstance(arg, str) and arg.startswith("$"):
            # Dans l'exemple utilisateur: {"id": "$VAR1"} ... memory["$VAR1"] = ...
            # Ou memory.get(variable_name).
            # Le prompt du planner disait: "id": "s1" ... "args": ["$s1"]
            # Si le planner met l'ID "s1", et référence "$s1", il faut gérer le '$'.
            
            # Convention: 
            # Si arg est "$s1", on cherche "s1" ou "$s1" dans la mémoire.
            # Pour simplifier, on stocke avec le nom fourni par le planner dans "id".
            # Si id="s1", memory["s1"] = val.
            # Si arg="$s1", on cherche "s1".
            
            key_to_find = arg[1:] # On enlève le '$'
            if key_to_find in self._storage:
                return self._storage[key_to_find]
            
            # Si on ne trouve pas sans le $, on essaie avec (si jamais l'id était "$VAR1")
            if arg in self._storage:
                return self._storage[arg]
                
            # Si pas trouvé, on renvoie None ou l'arg ? 
            # L'utilisateur dit: "Si ... ne trouve rien ... il doit arrêter tout de suite".
            # Pour l'instant on renvoie l'arg et on laissera l'appelant gérer ou lever une erreur.
            raise ValueError(f"Variable '{arg}' non trouvée en mémoire. Echec de la résolution.")
            
        return arg

    def resolve_args(self, args: List[Any]) -> List[Any]:
        return [self.resolve(arg) for arg in args]

    def dump(self) -> Dict[str, Any]:
        return self._storage
