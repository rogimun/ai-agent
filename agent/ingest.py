import os
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from shared.config import settings

def vectorize_documents():
    pdf_loader = DirectoryLoader("./data", glob="*.pdf", loader_cls=PyPDFLoader)
    
    docs = pdf_loader.load()
    print(f"{len(docs)}개의 문서를 불러왔습니다.")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,    # 한 조각에 최대 500자
        chunk_overlap=50   # 조각 간의 문맥 연결을 위해 50자 겹침
    )
    splits = text_splitter.split_documents(docs)
    print(f"문서를 {len(splits)}개의 조각으로 나누었습니다.")

    embeddings = OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            api_key=settings.OPENAI_API_KEY,
        )
    
    vector_db = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory="./db/chroma_db"
    )
    
    print("벡터화 완료! DB에 저장되었습니다.")

if __name__ == "__main__":
    vectorize_documents()