from langchain.vectorstores import VectorStore
from langchain.schema import Document
from data_preparation_modules import DataPreparationModules
from common import CommonModules
import asyncio
import time


class Pipeline:
    def __new__(cls, *args, **kwargs):
        raise NotImplementedError("This class is not instantiable")

    @classmethod
    def run(cls, *args, **kwargs):
        raise NotImplementedError

class DataPreparationPipeline(Pipeline):
    @classmethod
    def run(
        cls,
        file_path: str,
        chunk_size: int,
        chunk_overlap: int,
        question_pre_context: str | None = None,
        answer_pre_context: str | None = None,
    ) -> tuple[list[Document], VectorStore]:
        chunks = DataPreparationModules.chunker(file_path, chunk_size, chunk_overlap)
        question_gen_start_time = time.perf_counter()
        chunks_with_questions = asyncio.run(DataPreparationModules.question_generator(
                chunks=chunks,
                question_pre_context=question_pre_context,
                answer_pre_context=answer_pre_context,
        ))
        question_gen_end_time = time.perf_counter()
        q_minutes, q_seconds = CommonModules.timer(question_gen_start_time, question_gen_end_time)
        print(f"Question generation took {q_minutes} minutes and {q_seconds} seconds.")
        return chunks_with_questions 