import os
import shutil
import uuid
from typing import Dict, Any, Tuple


class VisionTool:
    """
    Agent 'Outil' encapsulant la logique de Computer Vision.
    """

    def __init__(self, output_dir: str = "../../../data/outputs"):
        # Chemin absolu basé sur l'emplacement du fichier
        base_path = os.path.dirname(__file__)
        self.output_dir = os.path.join(base_path, output_dir)
        os.makedirs(self.output_dir, exist_ok=True)

    def detect_tumor(
        self, image_path: str, scenario_id: str, llm_client=None
    ) -> Dict[str, Any]:
        """
        Wrapper principal appelé par le Coordinateur.

        Args:
            image_path: Chemin vers l'image mammographie.
            llm_client: Instance de LLMClient pour logger le coût 'fictif' de l'outil vision.
        """
        # On loggue l'appel comme si c'était un service API coûteux
        if llm_client:
            call_id = str(uuid.uuid4())
            # On simule 1000 tokens in, 50 out pour le coût du modèle vision
            llm_client.log_metric(
                scenario_id,
                call_id,
                "vision_tool_v1",
                1000,
                50,
                450.0,
                "SUCCESS",
                "Vision Tool Inference",
            )

        # Appel du code technique interne
        annotated_path, summary, confidence = self._process_image_internal(image_path)

        return {
            "status": "success",
            "annotated_image": annotated_path,
            "clinical_summary": summary,
            "confidence_score": confidence,
        }

    def _process_image_internal(self, image_path: str) -> Tuple[str, str, float]:
        """
        PLACEHOLDER: Collez votre code OpenCV / PaliGemma ici.
        """
        # --- VOTRE CODE DÉMARRE ICI ---
        # TODO: Charger image, inférence modèle, dessiner Bounding Box

        filename = os.path.basename(image_path)
        output_path = os.path.join(self.output_dir, f"annotated_{filename}")

        # Simulation : copie simple de l'image
        try:
            shutil.copy(image_path, output_path)
        except Exception as e:
            print(f"Erreur copie image: {e}")

        # Simulation de résultats
        detected = True
        confidence = 0.89

        if detected:
            summary = "Opacité nodulaire dense détectée dans le quadrant supéro-externe. Classification BIRADS suggérée: 4."
        else:
            summary = (
                "Aucune anomalie significative détectée. Tissus mammaires normaux."
            )

        # --- VOTRE CODE S'ARRÊTE ICI ---

        return output_path, summary, confidence
