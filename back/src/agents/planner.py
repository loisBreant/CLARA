import json
from core.llm_client import OllamaClient 

class PlannerAgent:
    def __init__(self, client: OllamaClient):
        self.client = client
        self.system_prompt = """
Tu es l'Architecte Clinique du système C.L.A.R.A.
Ta tâche est de PLANIFIER l'analyse d'un dossier patient, mais NE PAS l'exécuter toi-même.

Voici les OUTILS disponibles pour l'Exécuteur :
1. VISION_TOOL(image_path) : Pour détecter une tumeur sur une radio.
2. GUIDELINE_TOOL(query) : Pour chercher des protocoles officiels (RAG).
3. STATS_TOOL(sql_query) : Pour comparer aux statistiques de la base de données (DuckDB).

Règles :
- Reçois le dossier patient et l'image en entrée.
- Décompose le problème en étapes logiques.
- Réponds UNIQUEMENT sous forme d'une liste JSON stricte.
- N'écris aucune phrase d'introduction ou de conclusion.

Format attendu :
[
  {"step": 1, "tool": "NOM_OUTIL", "args": "argument_pour_outil", "description": "Pourquoi je fais ça"},
  {"step": 2, "tool": "NOM_OUTIL", "args": "...", "description": "..."},
  {"step": 3, "tool": "NO_TOOL", "args": "Synthèse", "description": "Rédiger le rapport final"}
] 
"""
    def generate_plan(self, patient_data: dict, image_path: str, scenario_id: str):
        # 1. Construction du message utilisateur
        user_msg = f"""
        NOUVEAU CAS PATIENT :
        Nom : {patient_data.get('nom')}
        Age : {patient_data.get('age')}
        Symptômes : {patient_data.get('symptomes')}
        Chemin Image : {image_path}
        
        Génère le plan d'action JSON.
        """

        # 2. Appel au LLM (Gemma 2)
        # On loggue l'appel ici pour le fichier costs.csv 
        response_text = self.client.call_model(
            prompt=user_msg, 
            system_instruction=self.system_prompt,
            scenario_id=scenario_id,
            call_id="planner_01"
        )

        # 3. Nettoyage et Parsing (Crucial avec les LLM locaux)
        try:
            # Parfois Gemma ajoute des ```json ... ```, on les retire
            clean_json = response_text.replace("```json", "").replace("```", "").strip()
            plan = json.loads(clean_json)
            return plan
        except json.JSONDecodeError:
            print(f"Erreur de format JSON du Planner: {response_text}")
            # Fallback : On retourne un plan par défaut de sécurité
            return [{"step": 1, "tool": "NO_TOOL", "args": "Erreur Planification", "description": "Echec du planner"}]