"""
recommender_service.py – Lightweight item-to-item recommender.

Loads a precomputed co-occurrence model from JSON and provides
fast, in-memory recommendations. No heavy ML frameworks required.
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)

RECOMMENDER_MODEL_FILE = Path(
    os.getenv("RECOMMENDER_MODEL_FILE", "data/recommender_model.json")
)


class RecommenderService:
    def __init__(self):
        self._model: Dict | None = None

    def load(self) -> bool:
        if not RECOMMENDER_MODEL_FILE.exists():
            logger.warning("Recommender model file not found: %s", RECOMMENDER_MODEL_FILE)
            self._model = None
            return False

        try:
            with open(RECOMMENDER_MODEL_FILE, "r", encoding="utf-8") as f:
                self._model = json.load(f)
            logger.info("Recommender model loaded from %s", RECOMMENDER_MODEL_FILE)
            return True
        except Exception as exc:
            logger.error("Failed to load recommender model: %s", exc)
            self._model = None
            return False

    @property
    def available(self) -> bool:
        return bool(self._model)

    def recommend_for_user(self, history: List[str], k: int = 5) -> List[str]:
        if not self._model:
            return []

        history = [str(h) for h in history if h]
        if not history:
            return self._fallback_popular(k)

        similar_map = self._model.get("similar", {})
        scores: Dict[str, float] = {}

        total = max(len(history), 1)
        for idx, item_id in enumerate(history):
            sim_list = similar_map.get(item_id, [])
            weight = (total - idx) / total
            for entry in sim_list:
                rec_id = str(entry.get("id"))
                if not rec_id or rec_id in history:
                    continue
                score = float(entry.get("score", 0)) * weight
                scores[rec_id] = scores.get(rec_id, 0.0) + score

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        results = [item_id for item_id, _ in ranked[:k]]
        if len(results) < k:
            results.extend([pid for pid in self._fallback_popular(k) if pid not in results])
        return results[:k]

    def _fallback_popular(self, k: int) -> List[str]:
        if not self._model:
            return []
        popular = self._model.get("popular", [])
        return [str(pid) for pid in popular[:k]]
