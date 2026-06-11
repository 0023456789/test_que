import pandas as pd
from neo4j import GraphDatabase

# --- CẤU HÌNH KẾT NỐI NEO4J ---
# Bạn hãy thay đổi thông tin này để khớp với database Neo4j của bạn
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password" 

class KBGraphBuilder:
    def __init__(self, uri, user, password):
        # Khởi tạo kết nối với driver Neo4j
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def build_graph_from_csv(self, csv_file):
        print(f"Đang đọc dữ liệu từ tệp {csv_file}...")
        df = pd.read_csv(csv_file)
        
        # Ánh xạ action sang Relationship Types trong Neo4j (Neo4j khuyên dùng viết hoa)
        action_mapping = {
            'view': 'VIEWED',
            'click': 'CLICKED',
            'add_to_cart': 'ADDED_TO_CART'
        }
        df['rel_type'] = df['action'].map(action_mapping)
        
        # Chuyển dataframe thành format list các dictionary để dùng với UNWIND (batching)
        records = df[['user_id', 'product_id', 'rel_type', 'timestamp']].to_dict('records')
        
        with self.driver.session() as session:
            # 1. Khởi tạo Constraints (Index) giúp tăng tốc độ MERGE và tránh trùng lặp
            print("Đang cấu trúc Constraints cho đồ thị...")
            session.run("CREATE CONSTRAINT kb_user_id IF NOT EXISTS FOR (u:User) REQUIRE u.user_id IS UNIQUE")
            session.run("CREATE CONSTRAINT kb_product_id IF NOT EXISTS FOR (p:Product) REQUIRE p.product_id IS UNIQUE")
            
            # 2. Xây dựng đồ thị (Graph nodes & relationships)
            print("Bắt đầu tạo các Node và Relationship cho KB_Graph...")
            session.execute_write(self._import_data, records)
            
        print("Đã hoàn tất xây dựng cấu trúc KB_Graph vào Neo4j!")

    @staticmethod
    def _import_data(tx, records):
        """
        Dùng Cypher và tham số để tách các query theo từng loại relationship.
        Chúng ta sẽ gắn nhãn (Label) :KB_Graph cho các Node để định danh cụm đồ thị này.
        """
        rel_types = ['VIEWED', 'CLICKED', 'ADDED_TO_CART']
        
        for rel in rel_types:
            # Lọc các danh sách dòng tương ứng với Loại Action hiện tại
            batch = [r for r in records if r['rel_type'] == rel]
            if not batch: 
                continue
            
            # Tạo Query Batching. MERGE đảm bảo Node hoặc Nhãn (Label) chỉ tạo 1 lần.
            query = f"""
            UNWIND $batch AS row
            MERGE (u:User:KB_Graph {{user_id: row.user_id}})
            MERGE (p:Product:KB_Graph {{product_id: row.product_id}})
            MERGE (u)-[r:{rel}]->(p)
            ON CREATE SET r.timestamp = row.timestamp
            """
            tx.run(query, batch=batch)

import time

if __name__ == "__main__":
    max_retries = 30
    for i in range(max_retries):
        try:
            builder = KBGraphBuilder(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
            builder.driver.verify_connectivity() # Kiểm tra kết nối trước
            
            # Đường dẫn tới tệp được tạo trước đó
            builder.build_graph_from_csv('data_user500.csv')
            builder.close()
            break
        except Exception as e:
            print(f"[{i+1}/{max_retries}] Đang đợi Neo4j khởi động...")
            time.sleep(2)
