import json
import os
from qdrant_client import QdrantClient
from qdrant_client.http import models
from langchain_gigachat.chat_models import GigaChat
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_qdrant import QdrantVectorStore
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """Ты — ведущий инженер-технолог железнодорожного транспорта.
Твоя задача: разработать максимально подробный и объемный текст для раздела "{section_name}" местной инструкции станции.

ИНСТРУКЦИЯ ПО ВЫПОЛНЕНИЮ:
1. Изучи ФАКТИЧЕСКИЕ ДАННЫЕ (техпаспорт в формате JSON) и РЕФЕРЕНСЫ.
2. Напиши текст нового раздела, СТРОГО КОПИРУЯ ОФИЦИАЛЬНО-ДЕЛОВОЙ СТИЛЬ, СТРУКТУРУ И ОБЪЕМ из РЕФЕРЕНСОВ.
3. Сохраняй все стандартные бюрократические формулировки, ссылки на ПТЭ, правила безопасности и общие абзацы, которые есть в референсах. Текст должен быть длинным и развернутым, как настоящий юридический документ.
4. Вплетай факты из ФАКТИЧЕСКИХ ДАННЫХ (названия, длины, вагоны) в этот длинный текст.
5. Отвечай ТОЛЬКО готовым текстом раздела.

ФАКТИЧЕСКИЕ ДАННЫЕ:
{passport_data}

РЕФЕРЕНСЫ:
{references}
"""

class StationInstructionAI:
    def __init__(self, gigachat_credentials: str, qdrant_url: str = "http://127.0.0.1:6333"):
        self.collection_name = "station_instructions"
        
        self.qdrant = QdrantClient(url=qdrant_url, timeout=60.0)
        
        self.embeddings = HuggingFaceEmbeddings(model_name="cointegrated/rubert-tiny2")
        
        self.llm = GigaChat(credentials=gigachat_credentials, verify_ssl_certs=False)

        self.vector_store = QdrantVectorStore(
            client=self.qdrant,
            collection_name=self.collection_name,
            embedding=self.embeddings
        )

    def _retrieve_references(self, query_text: str, section_name: str, k: int = 7) -> str:
        if not self.qdrant.collection_exists(self.collection_name):
            return "Референсы отсутствуют."
        
        filter_obj = models.Filter(
            must=[
                models.FieldCondition(
                    key="metadata.section_name",
                    match=models.MatchValue(value=section_name)
                )
            ]
        )
        
        results = self.vector_store.similarity_search(
            query=query_text, 
            k=k,
            filter=filter_obj 
        )
        
        if not results:
            return "Точных референсов не найдено."
            
        return "\n\n---\n\n".join([doc.page_content for doc in results])

    def generate_section(self, section_name: str, passport_data: dict) -> str:
        passport_context = json.dumps(passport_data, ensure_ascii=False)
        
        references_text = self._retrieve_references(passport_context, section_name)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("user", "Сгенерируй текст для раздела: {section_name}")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        
        return chain.invoke({
            "section_name": section_name,
            "passport_data": passport_context,
            "references": references_text
        })