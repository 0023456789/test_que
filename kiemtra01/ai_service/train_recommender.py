"""
Train a lightweight item-to-item co-occurrence recommender.

This script reads user interactions from a CSV file (user_id, product_id, action)
and writes a compact JSON model for fast inference.
"""

import argparse
import csv
import json
import math
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set

ACTION_WEIGHTS = {
    "view": 1.0,
    "click": 2.0,
    "add_to_cart": 3.0,
    "purchase": 4.0,
}


def load_catalog_ids(catalog_path: Path) -> Set[str]:
    if not catalog_path.exists():
        return set()
    try:
        with open(catalog_path, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except Exception:
        return set()

    if isinstance(payload, dict):
        items = payload.get("items", [])
    else:
        items = payload

    ids = set()
    if isinstance(items, list):
        for item in items:
            if not isinstance(item, dict):
                continue
            product_id = item.get("product_id")
            if not product_id and item.get("id") is not None:
                try:
                    product_id = f"P{int(item.get('id')):03d}"
                except (TypeError, ValueError):
                    product_id = None
            if product_id:
                ids.add(str(product_id))
    return ids


def read_interactions(csv_path: Path, allowed_ids: Set[str]) -> Dict[str, Dict[str, float]]:
    user_items: Dict[str, Dict[str, float]] = defaultdict(dict)

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            user_id = (row.get("user_id") or "").strip()
            product_id = (row.get("product_id") or "").strip()
            action = (row.get("action") or "view").strip().lower()

            if not user_id or not product_id:
                continue
            if allowed_ids and product_id not in allowed_ids:
                continue

            weight = ACTION_WEIGHTS.get(action, 1.0)
            prev = user_items[user_id].get(product_id, 0.0)
            user_items[user_id][product_id] = prev + weight

    return user_items


def build_model(user_items: Dict[str, Dict[str, float]], top_k: int) -> Dict:
    item_counts: Dict[str, float] = defaultdict(float)
    co_counts: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))

    for _, items in user_items.items():
        keys = list(items.keys())
        for i, item_i in enumerate(keys):
            weight_i = items[item_i]
            item_counts[item_i] += weight_i
            for j in range(i + 1, len(keys)):
                item_j = keys[j]
                weight_j = items[item_j]
                score = weight_i * weight_j
                co_counts[item_i][item_j] += score
                co_counts[item_j][item_i] += score

    similar = {}
    for item_i, neighbors in co_counts.items():
        sims = []
        for item_j, co in neighbors.items():
            denom = math.sqrt(item_counts[item_i] * item_counts[item_j])
            if denom <= 0:
                continue
            sims.append({"id": item_j, "score": round(co / denom, 6)})
        sims.sort(key=lambda x: x["score"], reverse=True)
        similar[item_i] = sims[:top_k]

    popular = sorted(item_counts.items(), key=lambda x: x[1], reverse=True)

    model = {
        "model_type": "item_cooccurrence",
        "version": 1,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "top_k": top_k,
        "items": sorted(item_counts.keys()),
        "item_counts": {k: round(v, 3) for k, v in item_counts.items()},
        "popular": [item_id for item_id, _ in popular],
        "similar": similar,
    }
    return model


def main():
    parser = argparse.ArgumentParser(description="Train a lightweight recommender model")
    base_dir = Path(__file__).resolve().parent

    parser.add_argument(
        "--input",
        default=os.getenv("RECOMMENDER_TRAIN_FILE", str(base_dir.parent / "data_user500.csv")),
        help="Path to interactions CSV",
    )
    parser.add_argument(
        "--output",
        default=os.getenv("RECOMMENDER_MODEL_FILE", str(base_dir / "data" / "recommender_model.json")),
        help="Where to write the model JSON",
    )
    parser.add_argument(
        "--catalog",
        default=os.getenv("PRODUCT_CATALOG_FILE", str(base_dir / "data" / "products.json")),
        help="Optional product catalog to filter product IDs",
    )
    parser.add_argument("--top-k", type=int, default=20, help="Top similar items to keep per item")

    args = parser.parse_args()

    csv_path = Path(args.input)
    if not csv_path.exists():
        raise SystemExit(f"Input CSV not found: {csv_path}")

    catalog_ids = load_catalog_ids(Path(args.catalog))
    user_items = read_interactions(csv_path, catalog_ids)

    if not user_items:
        raise SystemExit("No interactions found after filtering.")

    model = build_model(user_items, top_k=args.top_k)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(model, f, indent=2)

    print(f"Saved model to {output_path}")
    print(f"Users: {len(user_items)} | Items: {len(model['items'])}")


if __name__ == "__main__":
    main()
