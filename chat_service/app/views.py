import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from langchain_community.graphs import Neo4jGraph
from langchain_community.chat_models import ChatOllama
from langchain_community.chains.graph_qa.cypher import GraphCypherQAChain
from langchain_core.prompts import PromptTemplate
from .serializers import ChatRequestSerializer

class ChatRAGView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            self.graph = Neo4jGraph(
                url="bolt://neo4j_apoc_db:7687",
                username="neo4j",
                password="password",
                sanitize=True
            )
            self.llm = ChatOllama(model="llama3.2:1b", base_url="http://ollama:11434")
            
            cypher_prompt_template = """You are an expert Neo4j Developer translating user questions into Cypher queries.
The knowledge graph schema is:
{schema}
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
            print(f"Error initializing RAG: {e}")

    def post(self, request, *args, **kwargs):
        serializer = ChatRequestSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            query = serializer.validated_data['query']
            
            try:
                if self.qa_chain:
                    rag_result = self.qa_chain.invoke({"query": query})
                    answer = rag_result.get('result', "Xin lỗi, tôi chưa thể trả lời câu hỏi này.")
                else:
                    answer = "RAG System Unavailable."
            except Exception as e:
                answer = f"Lỗi truy vấn: {str(e)}"
                
            suggested_products = ["P001", "P005"]

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
        
        related_products_predictions = ["P100", "P101", "P102"]
        message = f"Bạn vừa chọn sản phẩm {product_id}, bạn có muốn xem thêm các sản phẩm liên quan không?"
        
        return Response({
            "message": message,
            "predictions": related_products_predictions,
            "status": 200
        })

