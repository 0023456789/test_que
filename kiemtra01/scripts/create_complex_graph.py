from neo4j import GraphDatabase
import random
import time

URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "password"

def create_constraints(tx):
    tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (u:User) REQUIRE u.user_id IS UNIQUE")
    tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (p:Product) REQUIRE p.product_id IS UNIQUE")

def fetch_category_ids(tx):
    res = tx.run("MATCH (c:Category) RETURN c.categoryID AS id LIMIT 100")
    return [r["id"] for r in res]

def batch_create(tx, query, params_list):
    for chunk_start in range(0, len(params_list), 1000):
        chunk = params_list[chunk_start:chunk_start+1000]
        tx.run(query, items=chunk)

def main():
    drv = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    with drv.session() as s:
        print("Creating constraints...")
        s.execute_write(create_constraints)

        categories = s.execute_read(fetch_category_ids)
        if not categories:
            print("No Category nodes found, creating sample categories...")
            cats = [ {"categoryID": str(i), "categoryName": f"Cat_{i}"} for i in range(1,11) ]
            s.write_transaction(batch_create,
                                "UNWIND $items AS c CREATE (:Category {categoryID: c.categoryID, categoryName: c.categoryName})",
                                cats)
            categories = [c["categoryID"] for c in cats]

        print(f"Using {len(categories)} categories")

        # Create users
        user_count = 200
        users = [{"user_id": f"user_{i:04d}", "name": f"User_{i}"} for i in range(1, user_count+1)]
        print(f"Creating {len(users)} users...")
        s.execute_write(batch_create,
                            "UNWIND $items AS u CREATE (usr:User {user_id: u.user_id, name: u.name})",
                            users)

        # Create products
        product_count = 500
        products = []
        for i in range(1, product_count+1):
            prod = {
                "product_id": f"P{i:05d}",
                "name": f"Product_{i}",
                "categoryID": random.choice(categories)
            }
            products.append(prod)

        print(f"Creating {len(products)} products...")
        s.execute_write(batch_create,
                            "UNWIND $items AS p MERGE (prod:Product {product_id: p.product_id}) SET prod.name = p.name, prod.categoryID = p.categoryID",
                            products)

        # Link products to categories
        print("Linking products to categories...")
        rels = []
        for p in products:
            rels.append({"pid": p["product_id"], "cid": p["categoryID"]})
        s.execute_write(batch_create,
                            "UNWIND $items AS x MATCH (prod:Product {product_id: x.pid}), (cat:Category {categoryID: x.cid}) MERGE (prod)-[:IN_CATEGORY]->(cat)",
                            rels)

        # Create interactions: VIEWED, CLICKED, ADDED_TO_CART
        print("Creating interaction relationships...")
        interactions = []
        for u in users:
            num_actions = random.randint(5, 40)
            for _ in range(num_actions):
                p = random.choice(products)
                t = random.choice(["VIEWED", "CLICKED", "ADDED_TO_CART"]) 
                interactions.append({"uid": u["user_id"], "pid": p["product_id"], "type": t, "ts": int(time.time())})

        print(f"Creating ~{len(interactions)} relationships...")
        # We'll create by type in batches
        for rel_type in ("VIEWED","CLICKED","ADDED_TO_CART"):
            items = [it for it in interactions if it["type"]==rel_type]
            if not items:
                continue
            q = f"UNWIND $items AS it MATCH (u:User {{user_id: it.uid}}), (p:Product {{product_id: it.pid}}) CREATE (u)-[:{rel_type} {{ts: it.ts}}]->(p)"
            s.execute_write(batch_create, q, items)

        # Add some richer structure: Reviews and Purchases as nodes connected to users and products
        print("Adding reviews and purchases...")
        reviews = []
        purchases = []
        for u in random.sample(users, k=min(50, len(users))):
            bought = random.sample(products, k=5)
            for p in bought:
                purchases.append({"uid": u["user_id"], "pid": p["product_id"], "amount": random.randint(1,5), "ts": int(time.time())})
                if random.random() < 0.6:
                    reviews.append({"uid": u["user_id"], "pid": p["product_id"], "rating": random.randint(1,5), "text": "Good product", "ts": int(time.time())})

        s.execute_write(batch_create,
                            "UNWIND $items AS it MATCH (u:User {user_id: it.uid}), (p:Product {product_id: it.pid}) CREATE (pur:Purchase {amount: it.amount, ts: it.ts}) CREATE (u)-[:MADE]->(pur)-[:OF]->(p)",
                            purchases)

        s.execute_write(batch_create,
                            "UNWIND $items AS it MATCH (u:User {user_id: it.uid}), (p:Product {product_id: it.pid}) CREATE (rev:Review {rating: it.rating, text: it.text, ts: it.ts}) CREATE (u)-[:WROTE]->(rev)-[:ABOUT]->(p)",
                            reviews)

        # Final stats
        stats = s.run("MATCH (n) RETURN labels(n) AS labels, count(n) AS c ORDER BY c DESC LIMIT 20").data()
        print("Top label counts:")
        for r in stats:
            print(r)

    drv.close()

if __name__ == '__main__':
    main()
