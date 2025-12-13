import sqlite3
import os
import re
import json
from typing import Dict, Any, List


class DatabaseTool:
    """
    Agent Data Analyst : SQL Generation + Visualization Advisory.
    """

    DB_PATH = os.path.join(os.path.dirname(__file__), "../../data/medical.db")

    SCHEMA_DESC = """
    Tables:
    - patients (id, patient_ref, age, risk_factor)
    - mammograms (id, patient_id, exam_date, birads_score, density, finding_type)
    """

    def __init__(self, llm_client):
        self.llm = llm_client

    def query_data(self, user_question: str, scenario_id: str) -> Dict[str, Any]:
        """
        1. Convertit Question -> SQL
        2. Exécute SQL
        3. Convertit Résultat -> Réponse Texte + Config Graphique
        """

        # --- PHASE 1 : GÉNÉRATION SQL ---
        prompt_sql = f"""
        Tu es un Data Analyst Expert.
        SCHÉMA : {self.SCHEMA_DESC}
        QUESTION : "{user_question}"
        
        Consignes :
        - Génère une requête SQL SQLite valide.
        - Pour des métriques, utilise AVG, COUNT, GROUP BY.
        - Ne donne QUE le code SQL brut (pas de markdown).
        """

        generated_sql = self.llm.generate(
            prompt=prompt_sql, scenario_id=scenario_id, notes="DataAnalyst: SQL Gen"
        )
        clean_sql = self._clean_sql(generated_sql)

        try:
            # --- PHASE 2 : EXÉCUTION ---
            rows, columns = self._execute_sql(clean_sql)

            # Conversion en liste de dictionnaires pour le Frontend
            data_dict = [dict(zip(columns, row)) for row in rows]

            # --- PHASE 3 : ANALYSE & VISUALISATION ---
            if not data_dict:
                return {
                    "status": "success",
                    "answer": "Aucune donnée trouvée.",
                    "chart": None,
                }

            # On demande au LLM comment visualiser ces données
            viz_config = self._recommend_visualization(
                user_question, columns, data_dict[:5], scenario_id
            )

            # On demande au LLM une synthèse textuelle
            answer = self._synthesize_answer(user_question, rows, scenario_id)

            return {
                "status": "success",
                "generated_sql": clean_sql,
                "data": data_dict,  # Données pour le DataFrame
                "chart": viz_config,  # Instructions de plot
                "answer": answer,  # Texte explicatif
            }

        except Exception as e:
            return {"status": "error", "error": str(e), "generated_sql": clean_sql}

    def _recommend_visualization(
        self,
        question: str,
        columns: List[str],
        sample_data: List[Dict],
        scenario_id: str,
    ) -> Dict[str, Any] | None:
        """
        Décide si on doit afficher un graphique et lequel.
        """
        # Si une seule ligne et un seul résultat (ex: un count total), pas de graph
        if len(sample_data) == 1 and len(columns) == 1:
            return None

        prompt_viz = f"""
        Je suis une UI Streamlit. J'ai un résultat de requête SQL.
        Question User : "{question}"
        Colonnes : {columns}
        Exemple de données : {json.dumps(sample_data)}
        
        Dois-je afficher un graphique ? 
        Si non, réponds JSON: {{"type": null}}
        Si oui, choisis le meilleur type parmi ["bar", "line", "pie", "scatter"].
        
        Réponds UNIQUEMENT le JSON valide (pas de code block).
        Exemple: {{"type": "bar", "x_axis": "age", "y_axis": "count"}}
        """

        try:
            resp = self.llm.generate(
                prompt_viz, scenario_id=scenario_id, notes="DataAnalyst: Viz Config"
            )
            # Nettoyage JSON basique
            resp = resp.replace("```json", "").replace("```", "").strip()
            return json.loads(resp)
        except Exception:
            return None  # Fallback pas de graph en cas d'erreur de parsing

    def _clean_sql(self, text: str) -> str:
        text = text.replace("```sql", "").replace("```", "").strip()
        if re.search(r"\b(DROP|DELETE|UPDATE|INSERT)\b", text, re.IGNORECASE):
            raise ValueError("Opérations d'écriture interdites.")
        return text

    def _execute_sql(self, sql: str):
        conn = sqlite3.connect(self.DB_PATH)
        cursor = conn.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        columns = [d[0] for d in cursor.description]
        conn.close()
        return results, columns

    def _synthesize_answer(self, question: str, results: List, scenario_id: str) -> str:
        prompt = f"""
        Question: {question}
        Données (SQL): {str(results)[:1000]}...
        Fais une phrase de conclusion analytique (moyenne, tendance, max/min).
        """
        return self.llm.generate(
            prompt, scenario_id=scenario_id, notes="DataAnalyst: Text Answer"
        )
