import pandas as pd
from neo4j import GraphDatabase
import time

# --- CẤU HÌNH KẾT NỐI NEO4J ---
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"

class KBGraphBuilder:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def build_graph_from_csv(self, csv_file):
        print(f"Đang đọc dữ liệu từ tệp {csv_file}...")
        df = pd.read_csv(csv_file)
        
        # Ánh xạ action sang Relationship Types
        action_mapping = {
            'view': 'VIEWED',
            'click': 'CLICKED',
            'add_to_cart': 'ADDED_TO_CART'
        }
        df['rel_type'] = df['action'].map(action_mapping)
        df = df.dropna(subset=['rel_type']) # Loại bỏ nếu có action không đúng chuẩn
        
        records = df[['user_id', 'product_id', 'rel_type', 'timestamp']].to_dict('records')
        
        with self.driver.session() as session:
            # 1. Khởi tạo Constraints (Index) giúp tránh trùng lặp và tăng tốc độ MERGE
            print("Đang cấu trúc Constraints cho đồ thị...")
            session.run("CREATE CONSTRAINT user_id_unique IF NOT EXISTS FOR (u:User) REQUIRE u.user_id IS UNIQUE")
            session.run("CREATE CONSTRAINT product_id_unique IF NOT EXISTS FOR (p:Product) REQUIRE p.product_id IS UNIQUE")
            
            # 2. Xóa các quan hệ cũ để làm mới hoàn toàn (Trường hợp các Node đang rời rạc / sai lệch)
            print("Làm sạch các dữ liệu quan hệ cũ (nếu có)...")
            session.run("MATCH ()-[r]->() DELETE r")
            
            # 3. Yêu cầu chính: Thêm Node bằng MERGE và nạp dữ liệu bằng batch processing
            print("Bắt đầu nạp dữ liệu bằng Batch Processing...")
            BATCH_SIZE = 2000
            total_records = len(records)
            
            for i in range(0, total_records, BATCH_SIZE):
                batch = records[i:i+BATCH_SIZE]
                session.execute_write(self._process_batch, batch)
                print(f" Đã nạp {min(i+BATCH_SIZE, total_records)}/{total_records} quan hệ...")
            
            # 4. In ra tổng số lượng
            self._print_statistics(session)

    @staticmethod
    def _process_batch(tx, batch):
        rel_types = ['VIEWED', 'CLICKED', 'ADDED_TO_CART']
        
        for rel in rel_types:
            sub_batch = [r for r in batch if r['rel_type'] == rel]
            if not sub_batch: 
                continue
            
            # Dùng MERGE cho các Node đảm bảo tính duy nhất.
            # Dùng CREATE cho Relationship vì 1 user có thể thực hiện 1 hành động nhiều lần ở các timestamp khác nhau.
            query = f"""
            UNWIND $batch AS row
            MERGE (u:User:KB_Graph {{user_id: row.user_id}})
            MERGE (p:Product:KB_Graph {{product_id: row.product_id}})
            CREATE (u)-[r:{rel} {{timestamp: row.timestamp}}]->(p)
            """
            tx.run(query, batch=sub_batch)
            
    def _print_statistics(self, session):
        node_count = session.run("MATCH (n:KB_Graph) RETURN COUNT(n) AS count").single()["count"]
        rel_count = session.run("MATCH ()-[r]->() RETURN COUNT(r) AS count").single()["count"]
        print("\n" + "="*40)
        print("THỐNG KÊ DATABASE SAU KHI NẠP (KB_Graph):")
        print(f"Tổng số Node: {node_count}")
        print(f"Tổng số Relationship: {rel_count}")
        print("="*40)

if __name__ == "__main__":
    max_retries = 10
    for i in range(max_retries):
        try:
            builder = KBGraphBuilder(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
            builder.driver.verify_connectivity()
            
            builder.build_graph_from_csv('data_user500.csv')
            builder.close()
            break
        except Exception as e:
            print(f"[{i+1}/{max_retries}] Đang đợi CSDL Neo4j...")
            time.sleep(2)