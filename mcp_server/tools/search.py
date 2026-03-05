from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from shared.config import settings

embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)
vector_db = Chroma(persist_directory="./db/chroma_db", embedding_function=embeddings)

# --- 리트리버 설정 ---
# 여기서 다양한 검색 전략을 설정할 수 있습니다.
retriever = vector_db.as_retriever(
    search_type="mmr",           # 결과 간 중복을 최소화 (다양성 확보)
    search_kwargs={
        "k": 3,                  # 가져올 문서 개수
        "fetch_k": 10,           # 후보군 10개를 뽑은 뒤 그중 k개를 선택
        "lambda_mult": 0.5       # 다양성 가중치 (0에 가까울수록 아주 다양한 문서)
    }
)

def retrieve_knowledge(query: str) -> str:
    """리트리버 객체를 사용하여 정보를 검색합니다."""
    try:
        # 리트리버 호출 (LangChain 표준 방식)
        docs = retriever.get_relevant_documents(query)
        
        if not docs:
            return "검색된 내부 정보가 없습니다."
        
        formatted_results = [
            f"[정보 {i}] (출처: {doc.metadata.get('source')}): {doc.page_content}"
            for i, doc in enumerate(docs, 1)
        ]
        return "\n\n".join(formatted_results)
    
    except Exception as e:
        return f"리트리버 실행 오류: {str(e)}"