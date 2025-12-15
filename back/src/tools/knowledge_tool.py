class KnowledgeTool:
    """
    Outil de recherche dans les guidelines cliniques (RAG simulé ou réel).
    """

    @staticmethod
    def search_guidelines(query: str) -> str:
        """
        Simule une recherche vectorielle ou mot-clé dans une base de connaissances.
        """
        # Dans un vrai projet, ici on ferait : vector_db.search(query)

        # Base de connaissances simulée
        if "BIRADS 4" in query.upper() or "MASSE" in query.upper():
            return (
                "GUIDELINES 2024 (HAS/ACR) :\n"
                "- ACR 4 (Anomalie suspecte) : Valeur prédictive positive de cancer entre 2% et 95%.டும்"
                "- Action requise : Preuve histologique indispensable (microbiopsie ou macrobiopsie)."
                "- Discordance radio-clinique : Si une masse est vue à l'image mais que l'examen clinique ou l'historique "
                "(ex: mastectomie) contredit, une vérification d'identité patient et de l'intégrité de l'image est requise."
            )
        elif "MASTECTOMIE" in query.upper():
            return (
                "GUIDELINES CHIRURGIE :\n"
                "- Mastectomie totale : Ablation complète de la glande mammaire."
                "- Suivi : Pas de mammographie du côté opéré, sauf en cas de reconstruction par lambeau avec doute clinique."
                "- Risque d'erreur : Une image montrant du tissu mammaire abondant sur un côté mastectomisé indique une erreur de dossier ou d'étiquetage."
            )
        else:
            return "Aucune guideline spécifique trouvée pour cette requête."
