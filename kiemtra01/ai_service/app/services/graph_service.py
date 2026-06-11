"""
graph_service.py – Neo4j graph queries for recommendation logic.

Keeps a single driver instance reused across requests (no per-request
connection overhead).
"""

import os
import logging
from typing import List, Dict, Any

from neo4j import GraphDatabase

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration from environment
# ---------------------------------------------------------------------------
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
NEO4J_USER_ID_FIELD = os.getenv("NEO4J_USER_ID_FIELD", "id")
NEO4J_PRODUCT_ID_FIELD = os.getenv("NEO4J_PRODUCT_ID_FIELD", "id")


def _safe_prop(name: str, fallback: str) -> str:
    cleaned = "".join(ch for ch in name if ch.isalnum() or ch == "_")
    return cleaned or fallback


class GraphService:
    """Thin wrapper around the Neo4j driver."""

    def __init__(self):
        self._driver = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def connect(self):
        """Open the driver (connection pool)."""
        try:
            self._driver = GraphDatabase.driver(
                NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)
            )
            self._driver.verify_connectivity()
            logger.info("Neo4j connected at %s", NEO4J_URI)
        except Exception as exc:
            # Non-fatal: service continues without graph features
            logger.warning("Neo4j unavailable – graph features disabled: %s", exc)
            self._driver = None

    def close(self):
        if self._driver:
            self._driver.close()

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------
    def get_user_preferred_categories(self, user_id: int) -> List[str]:
        """
        Return the categories a user has interacted with most.

        Cypher pattern assumed in Neo4j:
            (:User {id: $user_id})-[:VIEWED|PURCHASED]->(:Product)-[:IN_CATEGORY]->(:Category)

        Falls back to an empty list when Neo4j is unavailable.
        """
        if self._driver is None:
            return []

        user_prop = _safe_prop(NEO4J_USER_ID_FIELD, "id")

        query = f"""
        MATCH (u:User {{{user_prop}: $user_id}})-[:VIEWED|PURCHASED]->(p:Product)-[:IN_CATEGORY]->(c:Category)
        RETURN c.name AS category, count(*) AS interactions
        ORDER BY interactions DESC
        LIMIT 5
        """
        try:
            with self._driver.session() as session:
                result = session.run(query, user_id=user_id)
                categories = [record["category"] for record in result]

                if not categories and isinstance(user_id, int) and user_prop != "id":
                    alt_user_id = f"user_{user_id:03d}"
                    result = session.run(query, user_id=alt_user_id)
                    categories = [record["category"] for record in result]

                return categories
        except Exception as exc:
            logger.error("Neo4j query error: %s", exc)
            return []

    def get_related_product_ids(self, product_ids: List[int]) -> List[int]:
        """
        Given a list of seed product IDs, return related product IDs via
        co-purchase / co-view edges.

        Cypher pattern:
            (:Product)-[:RELATED_TO]->(:Product)
        """
        if self._driver is None or not product_ids:
            return []

        product_prop = _safe_prop(NEO4J_PRODUCT_ID_FIELD, "id")
        query = f"""
        MATCH (p:Product)-[:RELATED_TO]->(related:Product)
        WHERE p.{product_prop} IN $product_ids
            AND NOT related.{product_prop} IN $product_ids
        RETURN DISTINCT related.{product_prop} AS related_id
        LIMIT 20
        """
        try:
            with self._driver.session() as session:
                result = session.run(query, product_ids=product_ids)
                return [record["related_id"] for record in result]
        except Exception as exc:
            logger.error("Neo4j query error: %s", exc)
            return []

    def get_user_recent_products(self, user_id: int, limit: int = 10) -> List[str]:
        """Return recent product IDs for a user based on interaction edges."""
        if self._driver is None:
            return []

        user_prop = _safe_prop(NEO4J_USER_ID_FIELD, "id")
        product_prop = _safe_prop(NEO4J_PRODUCT_ID_FIELD, "id")

        def _run_query(user_value: str | int, prod_prop: str) -> List[str]:
            query = f"""
            MATCH (u:User {{{user_prop}: $user_id}})-[r:VIEWED|CLICKED|ADDED_TO_CART|PURCHASED]->(p:Product)
            RETURN p.{prod_prop} AS product_id, r.timestamp AS ts
            ORDER BY ts DESC
            LIMIT $limit
            """
            with self._driver.session() as session:
                result = session.run(query, user_id=user_value, limit=limit)
                return [str(record["product_id"]) for record in result if record.get("product_id")]

        try:
            results = _run_query(user_id, product_prop)

            if not results and product_prop != "product_id":
                results = _run_query(user_id, "product_id")

            if not results and isinstance(user_id, int) and user_prop != "id":
                alt_user_id = f"user_{user_id:03d}"
                results = _run_query(alt_user_id, product_prop)
                if not results and product_prop != "product_id":
                    results = _run_query(alt_user_id, "product_id")

            return results
        except Exception as exc:
            logger.error("Neo4j query error: %s", exc)
            return []

    # ------------------------------------------------------------------
    # Example: seed sample graph data (call once from a setup script)
    # ------------------------------------------------------------------
    def seed_sample_data(self, products: List[Dict[str, Any]]):
        """
        Populate Neo4j with sample Product/Category nodes and dummy
        User interactions.  Idempotent – uses MERGE.
        """
        if self._driver is None:
            return

        with self._driver.session() as session:
            for p in products:
                session.run(
                    """
                    MERGE (cat:Category {name: $category})
                    MERGE (prod:Product {id: $id})
                      ON CREATE SET prod.name = $name, prod.price = $price
                    MERGE (prod)-[:IN_CATEGORY]->(cat)
                    """,
                    id=p["id"],
                    name=p["name"],
                    price=float(p["price"]),
                    category=p["category"],
                )
