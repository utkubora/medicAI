import os
from langchain.schema import Document
from generation import SimilarGeneration
from pathlib import Path
from base import StaticClass
from dotenv import load_dotenv, find_dotenv
import openai
from typing import Optional

OPENAI_CHAT_COMPLETION = 'gpt-3.5-turbo'
load_dotenv(find_dotenv())

# transformer model
from sentence_transformers.SentenceTransformer import SentenceTransformer

SIMILARITY_MODEL = "sentence-transformers/paraphrase-mpnet-base-v2"

# openai
from langchain.llms import OpenAI

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
openai_llm = OpenAI(model_name="text-davinci-003", temperature=0.0)

similarity_model = SentenceTransformer(SIMILARITY_MODEL)
similar_gen = SimilarGeneration(
    similarity_model=similarity_model,
)

class DataPreparationModules(StaticClass):
    """
    Static class to prepare dataset with perturbations.
    """

    @classmethod
    def chunker(cls, directory_path: Path, chunk_size: int, chunk_overlap: int) -> list[Document]:
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain_community.document_loaders.pdf import PyPDFLoader
        loader = PyPDFLoader(directory_path)
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
        docs = text_splitter.split_documents(documents)
        print("Loading documents from folder... Done.")
        return docs

    @classmethod
    async def question_generator(
        cls,
        chunks: list[Document],
        question_pre_context: str | None,
        answer_pre_context: str | None,
        model: str = OPENAI_CHAT_COMPLETION,
        temperature: float = 0.0,
        api_version: Optional[str] = None,
    ) -> list[Document]:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        engine = None
        if openai.api_type == "azure":
            engine = model
            api_version = api_version
        documents = []
        print("Creating question/answer pairs based on chunks...")
        pointer = 1
        for chunk in chunks:
            print(pointer)
            print(chunk)
            pointer += 1
            input = '"{chunk}"'.format(chunk=chunk.page_content)
            question_prompt = question_pre_context + input
            answer_prompt = answer_pre_context + input
            question_payload = [{"role": "user", "content": question_prompt}]
            answer_payload = [{"role": "user", "content": answer_prompt}]
            print("Creating prompt...")
            prompt = await openai.ChatCompletion.acreate(
                    model=model,
                    messages=question_payload,
                    temperature=temperature,
                    engine=engine,
                    api_version=api_version,
            )
            print("Creating answer...")
            answer = await openai.ChatCompletion.acreate(
                    model=model,
                    messages=answer_payload,
                    temperature=temperature,
                    engine=engine,
                    api_version=api_version,
            )
            print("Metadata entry...")
            metadata_entry = {
                    "question": prompt["choices"][0]["message"]["content"],
                    "answer": answer["choices"][0]["message"]["content"],
            }
            document = Document(page_content=chunk.page_content, metadata=metadata_entry)
            print("Appending metadata entry...")
            documents.append(document)
        print("Creating question/answer pairs based on chunks...Done.")
        return documents
    
