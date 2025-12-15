import time
import csv
import os
import uuid
import requests
from datetime import datetime


class LLMClient:
    """
    Client centralisé pour Ollama avec logging conforme aux exigences du projet (Page 5).
    """

    # Coût arbitraire pour la simulation (ex: $0.20 / 1M tokens)
    COST_PER_1M_TOKENS = 0.20
    # Chemin absolu ou relatif stable pour les logs
    LOG_FILE = os.path.join(os.path.dirname(__file__), "../../../data/logs/costs.csv")

    def __init__(
        self, model_name: str = "gemma2:9b", base_url: str = "http://localhost:11434"
    ):
        self.model_name = model_name
        self.base_url = base_url
        self._init_log_file()

    def _init_log_file(self):
        """Initialise le fichier CSV avec les headers requis par le sujet."""
        os.makedirs(os.path.dirname(self.LOG_FILE), exist_ok=True)
        if not os.path.exists(self.LOG_FILE):
            with open(self.LOG_FILE, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                # Champs requis par le PDF (Page 5) + cost_usd pour l'analyse
                writer.writerow(
                    [
                        "timestamp",
                        "scenario_id",
                        "call_id",
                        "model",
                        "endpoint",
                        "prompt_tokens",
                        "completion_tokens",
                        "total_tokens",
                        "latency_ms",
                        "status",
                        "notes",
                        "estimated_cost_usd",
                    ]
                )

    def log_metric(
        self,
        scenario_id: str,
        call_id: str,
        endpoint: str,
        p_tok: int,
        c_tok: int,
        latency: float,
        status: str,
        notes: str,
    ):
        """Enregistre une entrée dans le CSV."""
        total_tokens = p_tok + c_tok
        cost = (total_tokens / 1_000_000) * self.COST_PER_1M_TOKENS

        with open(self.LOG_FILE, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    datetime.now().isoformat(),
                    scenario_id,
                    call_id,
                    self.model_name,
                    endpoint,
                    p_tok,
                    c_tok,
                    total_tokens,
                    f"{latency:.2f}",
                    status,
                    notes,
                    f"{cost:.6f}",
                ]
            )

    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        scenario_id: str = "default",
        notes: str = "",
    ) -> str:
        """
        Appel synchrone à Ollama avec mesure de performance.
        Args:
            notes: Peut contenir le nom de l'agent (ex: 'Coordinator', 'Critic')
        """
        call_id = str(uuid.uuid4())
        start_time = time.time()
        endpoint = "/api/generate"

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": {"temperature": 0.1},  # Température basse pour rigueur médicale
        }

        try:
            response = requests.post(f"{self.base_url}{endpoint}", json=payload)
            response.raise_for_status()
            data = response.json()

            content = data.get("response", "")

            # Récupération des métriques réelles d'Ollama
            # Fallback sur une estimation len/3 si Ollama ne renvoie pas les stats
            p_tok = data.get("prompt_eval_count", len(prompt) // 3)
            c_tok = data.get("eval_count", len(content) // 3)

            latency_ms = (time.time() - start_time) * 1000

            self.log_metric(
                scenario_id,
                call_id,
                endpoint,
                p_tok,
                c_tok,
                latency_ms,
                "SUCCESS",
                notes,
            )

            return content

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            self.log_metric(
                scenario_id,
                call_id,
                endpoint,
                0,
                0,
                latency_ms,
                "ERROR",
                f"{notes} - Error: {str(e)}",
            )
            print(f"Error calling Ollama: {e}")
            return f"Error: {str(e)}"
