import json
import os
import sys
from typing import Dict, Any

# Hack pour imports relatifs si lancé depuis un script externe
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

# class OncologyAgentSystem:
#     def __init__(self, scenario_id: str):
#         self.llm = LLMClient()
#         self.vision = VisionTool()
#         self.knowledge = KnowledgeTool()
#         self.db_tool = DatabaseTool(self.llm)
#         self.scenario_id = scenario_id
#
#     def run_chat_mode(self, user_question: str) -> Dict[str, Any]:
#         """
#         Mode 'Chat with Data' : Interroge la base SQL.
#         """
#         print(f"[{self.scenario_id}] 🤖 Data Agent activé : {user_question}")
#         return self.db_tool.query_data(user_question, self.scenario_id)
#
#     def run_pipeline(
#         self, image_path: str, patient_data: Dict[str, Any], status_callback=None
#     ) -> Dict[str, Any]:
#         """
#         Orchestration complète avec reporting de statut en temps réel.
#         """
#
#         def report(msg):
#             print(f"[{self.scenario_id}] {msg}")
#             if status_callback:
#                 status_callback(msg)
#
#         # --- ÉTAPE 1 : PERCEPTION & EXÉCUTION (Vision) ---
#         report("ÉTAPE 1/4 : L'Agent Vision analyse l'image (OpenCV/DL)...")
#         vision_result = self.vision.detect_tumor(image_path, self.scenario_id, self.llm)
#
#         # --- ÉTAPE 2 : PLANIFICATION & RECHERCHE (Coordinator) ---
#         report("ÉTAPE 2/4 : Le Coordinateur consulte les Guidelines Médicales...")
#
#         findings = vision_result["clinical_summary"]
#         history = ", ".join(patient_data.get("surgical_history", []))
#
#         query = f"Management of {findings}. Context: {history}"
#         guidelines = self.knowledge.search_guidelines(query)
#
#         # --- ÉTAPE 3 : SYNTHÈSE (Coordinator) ---
#         report("ÉTAPE 3/4 : Le Coordinateur rédige le rapport diagnostique...")
#
#         prompt_coordinator = f"""
#         Tu es un Oncologue Expert.
#         
#         CONTEXTE PATIENT:
#         - Age: {patient_data.get("age")}
#         - Historique Chirurgical: {patient_data.get("surgical_history")}
#         
#         ANALYSE IMAGE (IA Vision):
#         - Résultat: {findings}
#         - Confiance: {vision_result["confidence_score"]}
#         
#         GUIDELINES MÉDICALES APPLICABLES:
#         {guidelines}
#         
#         TÂCHE:
#         Rédige un compte-rendu diagnostique préliminaire concis.
#         Analyse la compatibilité entre l'image et l'historique patient.
#         """
#
#         preliminary_report = self.llm.generate(
#             prompt=prompt_coordinator,
#             system_prompt="Tu es un assistant médical précis et factuel.",
#             scenario_id=self.scenario_id,
#             notes="Agent: Coordinator - Synthesis Step",
#         )
#
#         # --- ÉTAPE 4 : CRITIQUE (Reflection Pattern) ---
#         report("ÉTAPE 4/4 : Le Critique (Garde-Fou) vérifie la sécurité...")
#
#         prompt_critic = f"""
#         Tu es un Auditeur de Sécurité Clinique (Safety Reviewer).
#         
#         Ton but unique est de valider la cohérence logique du rapport ci-dessous.
#         
#         DONNÉES D'ENTRÉE :
#         1. Dossier Patient : {json.dumps(patient_data)}
#         2. Résultat Brut Vision : {vision_result["clinical_summary"]}
#         3. Rapport Proposé : {preliminary_report}
#         
#         INSTRUCTIONS :
#         - Vérifie si le rapport contredit l'historique chirurgical (ex: détection de tumeur sur un sein absent/mastectomisé).
#         - Vérifie si la confiance de l'IA Vision est suffisante (> 0.8) pour affirmer un diagnostic.
#         
#         FORMAT DE RÉPONSE :
#         Commence ta réponse par "STATUT: VALIDE" ou "STATUT: REJETÉ".
#         Ensuite, explique ton raisonnement en une phrase.
#         """
#
#         critique_result = self.llm.generate(
#             prompt=prompt_critic,
#             system_prompt="Tu es un critique rigoureux. Tu ne laisses rien passer.",
#             scenario_id=self.scenario_id,
#             notes="Agent: Critic - Reflection Step",
#         )
#
#         is_rejected = (
#             "REJETÉ" in critique_result.upper() or "REJECTED" in critique_result.upper()
#         )
#
#         report("Analyse terminée.")
#
#         return {
#             "vision_output": vision_result,
#             "guidelines_used": guidelines,
#             "preliminary_report": preliminary_report,
#             "critique": critique_result,
#             "final_status": "REJECTED" if is_rejected else "VALIDATED",
#         }
