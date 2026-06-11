import os
from langchain_community.graphs import Neo4jGraph
from langchain_community.chat_models import ChatOllama
from langchain_community.chains.graph_qa.cypher import GraphCypherQAChain
from langchain_core.prompts import PromptTemplate

# 1. Cấu hình kết nối Neo4j
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"

# Khởi tạo đối tượng Graph kết nối với CSDL
try:
    graph = Neo4jGraph(
        url=NEO4J_URI,
        username=NEO4J_USER,
        password=NEO4J_PASSWORD
    )
    graph.refresh_schema()
except Exception as e:
    print(f"Lỗi khởi tạo kết nối Neo4j: {e}")
    graph = None


# 2. Cấu hình LLM qua Ollama
llm = ChatOllama(model="qwen2.5:0.5b", temperature=0)

# 3. Tạo PromptTemplate theo cấu trúc Few-shot
cypher_prompt_template = """You are an expert Neo4j Developer translating user questions into Cypher queries.
The knowledge graph has nodes of type User (property: user_id) and Product (property: product_id).
Users interact with products via relationships: :VIEWED, :CLICKED, :ADDED_TO_CART.

Here are some examples to guide you:

Example 1:
Question: 'User 1 đã xem gì?'
Cypher: MATCH (u:User {{user_id: 'user_001'}})-[:VIEWED]->(p:Product) RETURN p.product_id

Example 2:
Question: 'Sản phẩm nào được thêm vào giỏ nhiều nhất?'
Cypher: MATCH ()-[r:ADDED_TO_CART]->(p:Product) RETURN p.product_id, count(r) ORDER BY count(r) DESC LIMIT 5

Example 3:
Question: 'User 5 đã click vào những sản phẩm nào?'
Cypher: MATCH (u:User {{user_id: 'user_005'}})-[:CLICKED]->(p:Product) RETURN p.product_id

Base on the above examples and the graph schema provided below, generate a valid Cypher query for the question.
Only return the Cypher query, without any explanations or markdown tags.

Schema:
{schema}

Question:
{question}

Cypher query:"""

cypher_prompt = PromptTemplate(
    input_variables=["schema", "question"], 
    template=cypher_prompt_template
)

# 4. Khởi tạo GraphCypherQAChain
if graph:
    qa_chain = GraphCypherQAChain.from_llm(allow_dangerous_requests=True, 
        cypher_llm=llm,
        qa_llm=llm,
        graph=graph,
        verbose=True,
        cypher_prompt=cypher_prompt,
        return_intermediate_steps=True
    )
else:
    qa_chain = None

# 5. Hàm thực thi quá trình Hỏi - Đáp với tính năng xử lý lỗi
def ask_question(user_question):
    print(f"\n[Câu hỏi]: {user_question}")
        
    if not qa_chain:
        return "[Lỗi hệ thống]: Không có đối tượng qa_chain. (Kết nối Neo4j hoặc Ollama chưa sẵn sàng)"
        
    try:
        response = qa_chain.invoke({"query": user_question})
        return f"[Trả lời]: {response['result']}"
    except Exception as e:
        return f"[Lỗi hệ thống]: Không thể truy vấn thông tin này. (Details: {str(e)})"

if __name__ == "__main__":
    questions = [
        "Sản phẩm nào được thêm vào giỏ nhiều nhất?",
        "User 010 đã xem những sản phẩm gì?",
        "Có bao nhiêu user đã click vào sản phẩm P001?"
    ]
    
    print("=== BẮT ĐẦU CHẠY HỆ THỐNG RAG VỚI Qwen & Neo4j ===")
    for q in questions:
        answer = ask_question(q)
        print(answer)
        print("-" * 50)
