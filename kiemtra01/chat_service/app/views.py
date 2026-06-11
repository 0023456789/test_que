import os
import re
import json
import time
import urllib.request
import urllib.error
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from langchain_community.graphs import Neo4jGraph
from langchain_community.chat_models import ChatOllama
from langchain_community.chains.graph_qa.cypher import GraphCypherQAChain
from langchain_core.prompts import PromptTemplate
from .serializers import ChatRequestSerializer
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model

try:
    recommender_model = load_model(os.path.join(settings.BASE_DIR, 'app', 'best_model.keras'))
except Exception as e:
    print(f"Khong the load model recommend: {e}")
    recommender_model = None

PRODUCT_NAMES = {
    "P001": "MacBook Pro 14 M3",
    "P002": "Dell XPS 14 Plus",
    "P003": "ASUS ROG Strix G16",
    "P004": "HP Omen 16 2026",
    "P005": "ThinkPad X1 Carbon Gen 12",
    "P006": "iPhone 16 Pro",
    "P007": "Samsung Galaxy S25 Ultra",
    "P008": "Xiaomi 15 Ultra",
    "P009": "OnePlus 13 Pro",
    "P010": "Google Pixel 9 Pro",
}

def get_product_name(pid: str) -> str:
    if pid in PRODUCT_NAMES:
        return PRODUCT_NAMES[pid]
    try:
        num = int(pid.replace("P", ""))
        categories = ["Smart TV", "Tai nghe Bluetooth", "Đồng hồ thông minh", "Tablet", "Loa không dây", "Chuột Game", "Bàn phím cơ", "Máy ảnh", "Màn hình", "Máy in"]
        brands = ["Sony", "Samsung", "Apple", "LG", "Asus", "Logitech", "Razer", "Canon", "Dell", "HP"]
        cat = categories[num % len(categories)]
        brand = brands[(num * 3) % len(brands)]
        return f"{cat} {brand} Mẫu {num}"
    except:
        return f"Sản phẩm {pid}"

class ChatRAGView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ai_chatbot_urls = [
            os.getenv("AI_CHATBOT_URL", "http://ai_service:8000/chatbot"),
            "http://host.docker.internal:8008/chatbot",
        ]
        self.graph = None
        self.qa_chain = None
        use_local_rag = os.getenv("USE_LOCAL_RAG", "false").lower() == "true"
        if not use_local_rag:
            return
        try:
            neo4j_url = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
            neo4j_user = os.getenv("NEO4J_USER", "neo4j")
            neo4j_password = os.getenv("NEO4J_PASSWORD", "password")
            ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
            ollama_model = os.getenv("OLLAMA_MODEL", "phi3.5")

            self.graph = Neo4jGraph(
                url=neo4j_url,
                username=neo4j_user,
                password=neo4j_password,
                sanitize=True
            )
            self.llm = ChatOllama(model=ollama_model, base_url=ollama_base_url)
            
            cypher_prompt_template = """You are an expert Neo4j Developer translating user questions into Cypher queries.
The knowledge graph schema is:
{schema}

Here are some examples to guide you:
Example 1:
Question: 'User 1 đã xem gì?'
Cypher: MATCH (u:User {{user_id: 'user_001'}})-[:VIEWED]->(p:Product) RETURN p.product_id

Example 2:
Question: 'Sản phẩm nào được thêm vào giỏ nhiều nhất?'
Cypher: MATCH ()-[r:ADDED_TO_CART]->(p:Product) RETURN p.product_id, count(r) ORDER BY count(r) DESC LIMIT 5

Example 3:
Question: 'Recommend laptop HP'
Cypher: MATCH (p:Product) WHERE p.product_id CONTAINS 'P' RETURN p.product_id LIMIT 5

Example 4:
Question: 'Sản phẩm nào bắt đầu bằng chữ P?'
Cypher: MATCH (p:Product) WHERE p.product_id STARTS WITH 'P' RETURN p.product_id LIMIT 5

Note: NEVER use the 'LIKE' operator in Cypher. Use 'CONTAINS' or 'STARTS WITH' instead.

Only return the Cypher query, without any explanations or markdown tags.
Question: {question}
Cypher query:"""
            self.cypher_prompt = PromptTemplate(
                input_variables=["schema", "question"],
                template=cypher_prompt_template
            )
            self.qa_chain = GraphCypherQAChain.from_llm(
                cypher_llm=self.llm,
                qa_llm=self.llm,
                graph=self.graph,
                verbose=True,
                cypher_prompt=self.cypher_prompt,
                allow_dangerous_requests=True
            )
        except Exception as e:
            self.qa_chain = None
            print(f"Local RAG disabled after init failure: {e}")

    def post(self, request, *args, **kwargs):
        serializer = ChatRequestSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            query = serializer.validated_data['query']
            
            try:
                if self.qa_chain:
                    rag_result = self.qa_chain.invoke({"query": query})
                    answer = rag_result.get('result', "Xin lá»—i, tÃ´i chÆ°a thá»ƒ tráº£ lá»i cÃ¢u há»i nÃ y.")
                    
                    # Convert any P001 to actual product names in the final answer
                    def replace_pid(match):
                        return get_product_name(match.group(0))
                    answer = re.sub(r'P\d+', replace_pid, answer)
                else:
                    payload = json.dumps({"message": query}).encode("utf-8")
                    answer = None
                    for url in self.ai_chatbot_urls:
                        for attempt in range(1, 4):
                            req = urllib.request.Request(
                                url,
                                data=payload,
                                headers={"Content-Type": "application/json"},
                                method="POST",
                            )
                            try:
                                with urllib.request.urlopen(req, timeout=20) as resp:
                                    data = json.loads(resp.read().decode("utf-8"))
                                answer = data.get("response", "Xin lá»—i, tÃ´i chÆ°a thá»ƒ tráº£ lá»i cÃ¢u há»i nÃ y.")
                                break
                            except Exception as err:
                                print(f"AI service fallback failed ({url}, attempt {attempt}): {err}")
                                time.sleep(1.0 * attempt)
                        if answer is not None:
                            break
                    if answer is None:
                        answer = "RAG System Unavailable."
            except Exception as e:
                answer = f"Lá»—i truy váº¥n: {str(e)}"
                
            # 1. FETCH USER HISTORY FROM NEO4J DB
            product_history = []
            suggested_products = []
            if hasattr(self, 'graph') and self.graph:
                try:
                    cypher_query = f"""
                    MATCH (u:User {{user_id: '{user_id}'}})-[r]->(p:Product)
                    WHERE type(r) IN ['VIEWED', 'CLICKED', 'ADDED_TO_CART']
                    RETURN p.product_id AS product_id
                    ORDER BY r.timestamp DESC LIMIT 4
                    """
                    res = self.graph.query(cypher_query)
                    product_history = [row['product_id'] for row in res]
                except Exception as e:
                    print(f"Error fetching user history from Neo4j: {e}")

            # 2. RUN RECOMMENDER MODEL WITH USER HISTORY
            if recommender_model and product_history:
                try:
                    seq = []
                    for p in product_history:
                        if p.startswith('P'):
                            try:
                                seq.append(int(p.replace('P', '')) - 1)
                            except:
                                pass
                    
                    if len(seq) > 0:
                        if len(seq) < 4:
                            seq = seq + [seq[-1]] * (4 - len(seq))
                        elif len(seq) > 4:
                            seq = seq[:4]

                        input_seq = np.array([seq])
                        preds = recommender_model.predict(input_seq, verbose=0)
                        top_3_indices = np.argsort(preds[0])[-3:][::-1]
                        suggested_products = [get_product_name(f"P{i+1:03d}") for i in top_3_indices]
                except Exception as e:
                    print(f"Error predicting recommendations: {e}")
            
            # 3. FALLBACK TO DATABASE (POPULAR PRODUCTS) IF MODEL RETURNS NOTHING
            if not suggested_products and hasattr(self, 'graph') and self.graph:
                try:
                    pop_query = "MATCH ()-[r:VIEWED]->(p:Product) RETURN p.product_id AS p_id, count(r) AS c ORDER BY c DESC LIMIT 3"
                    res = self.graph.query(pop_query)
                    suggested_products = [get_product_name(row['p_id']) for row in res]
                except:
                    pass

            return Response({
                "answer": answer,
                "suggested_products": suggested_products,
                "status": 200
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductActionSignalView(APIView):
    def post(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        action = request.data.get('action')

        related_products_predictions = []
        if recommender_model and product_id and product_id.startswith('P'):
            try:
                # Chuyen doi P001 sang 0
                product_code = int(product_id.replace('P', '')) - 1
                seq = np.array([[product_code, product_code, product_code, product_code]])
                preds = recommender_model.predict(seq, verbose=0)
                # Lay 3 class cao nhat
                top_3_indices = np.argsort(preds[0])[-3:][::-1]
                related_products_predictions = [get_product_name(f"P{i+1:03d}") for i in top_3_indices]
            except Exception as e:
                print(f"Loi du doan: {e}")
                related_products_predictions = []
        else:
            related_products_predictions = []

        message = f"Bạn vừa chọn mục này, bạn có muốn xem thêm các sản phẩm liên quan không?"

        return Response({
            "message": message,
            "predictions": related_products_predictions,
            "status": 200
        })
