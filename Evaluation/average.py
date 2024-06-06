from sentence_transformers import SentenceTransformer
from sentence_transformers import util as sent_util
import math
import numpy as np
import sys
from typing import Any, List, Optional, Dict, Literal
import os
from langchain.llms import OpenAI
import openai
from dotenv import load_dotenv, find_dotenv
import asyncio
import pandas as pd

load_dotenv(find_dotenv())
# os.environ["OPENAI_API_KEY"] = "API_KEY"
openai_llm = OpenAI(model_name="text-davinci-003", temperature=0.0)


DEFAULT_SENTENCE_XFMR = "sentence-transformers/paraphrase-mpnet-base-v2"


def load_similarity_model(
    model_name: str = DEFAULT_SENTENCE_XFMR,
    device: str = "cpu",
):
    sent_xfmer = SentenceTransformer(
        model_name,
        device=device,
    )
    return sent_xfmer


def compute_similarity(
    sentence_model: SentenceTransformer,
    reference_sentence: str,
    ground_truth_answer: str,
):
    ref_emb = sentence_model.encode(sentences=[reference_sentence], convert_to_tensor=True)
    ground_truth_emb = sentence_model.encode(sentences=[ground_truth_answer], convert_to_tensor=True)
    score = sent_util.cos_sim(ref_emb, ground_truth_emb)
    return score.cpu().numpy()[0][0]


def compute_euc_dist(
    sentence_model: SentenceTransformer,
    reference_sentence: str,
    ground_truth_answer: str,
):
    ref_emb = sentence_model.encode(sentences=[reference_sentence], convert_to_numpy=True)
    ground_truth_emb = sentence_model.encode(sentences=[ground_truth_answer], convert_to_numpy=True)
    euclidean_distance = np.linalg.norm(ref_emb - ground_truth_emb)
    return euclidean_distance


def compute_perplexity(
    sentence_model: SentenceTransformer,
    reference_sentence: str,
    ground_truth_answer: str,
):
    ref_emb = sentence_model.encode(sentences=[reference_sentence], convert_to_numpy=True)
    ground_truth_emb = sentence_model.encode(sentences=[ground_truth_answer], convert_to_numpy=True)
    perp_ref = math.exp(-np.mean(ref_emb))
    perp_truth = math.exp(-np.mean(ground_truth_emb))
    return [perp_ref, perp_truth]


def compute_relevancy(
    prompt: str,
    response: str,
):
    input = "Question: " + prompt + " Answer: " + response
    relevancy = asyncio.run(is_relevant(input=input))
    return relevancy


async def is_relevant(
        input: str,
        model: str = 'gpt-3.5-turbo',
        temperature: float = 0.0,
        api_version: Optional[str] = None,
    ) -> int:
    """Get generation from the model"""
    openai.api_key = os.getenv("OPENAI_API_KEY")
    engine = None
    if openai.api_type == "azure":
        engine = model
        api_version = api_version
    pre_context = "Only say 1 if this response contains the answer to the question, say 0 if the response does not contain the answer."
    prompt = input + pre_context
    payload = [{"role": "user", "content": prompt}]
    response = await openai.ChatCompletion.acreate(
        model=model,
        messages=payload,
        temperature=temperature,
        engine=engine,
        api_version=api_version,
    )
    return int(response["choices"][0]["message"]["content"])


async def get_ground_truth_answer(question: str, model: str = 'gpt-3.5-turbo') -> str:
    """Get ground truth answer from ChatGPT"""
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = await openai.ChatCompletion.acreate(
        model=model,
        messages=[{"role": "user", "content": question}],
        temperature=0.0,
    )
    return response["choices"][0]["message"]["content"]


def evaluate_answer(
    question: str,
    provided_answer: str,
    sentence_model: SentenceTransformer,
):
    # Get ground truth answer from ChatGPT
    ground_truth_answer = asyncio.run(get_ground_truth_answer(question))
    
    # Compute similarity
    similarity_score = compute_similarity(sentence_model, ground_truth_answer, provided_answer)
    
    # Compute Euclidean distance
    euc_distance = compute_euc_dist(sentence_model, ground_truth_answer, provided_answer)
    
    # Compute perplexity
    perplexity_scores = compute_perplexity(sentence_model, ground_truth_answer, provided_answer)
    
    # Compute relevancy
    relevancy = compute_relevancy(question, provided_answer)
    
    return {
        "question": question,
        "provided_answer": provided_answer,
        "ground_truth_answer": ground_truth_answer,
        "similarity_score": similarity_score,
        "euclidean_distance": euc_distance,
        "perplexity_scores": perplexity_scores,
        "relevancy": relevancy
    }


def evaluate_from_csv(file_path: str):
    # Load the CSV file
    df = pd.read_csv(file_path)
    
    # Load the similarity model
    model = load_similarity_model()
    
    # Initialize metrics
    total_similarity = 0
    total_euclidean_distance = 0
    total_perplexity_ref = 0
    total_perplexity_truth = 0
    total_relevancy = 0
    
    num_rows = len(df)
    
    # Evaluate each question-answer pair
    for index, row in df.iterrows():
        question = row['question']
        provided_answer = row['answer']
        
        metrics = evaluate_answer(question, provided_answer, model)
        
        total_similarity += metrics['similarity_score']
        total_euclidean_distance += metrics['euclidean_distance']
        total_perplexity_ref += metrics['perplexity_scores'][0]
        total_perplexity_truth += metrics['perplexity_scores'][1]
        total_relevancy += metrics['relevancy']
        
        print(f"Evaluation for row {index + 1}: {metrics}")
    
    # Compute average metrics
    avg_similarity = total_similarity / num_rows
    avg_euclidean_distance = total_euclidean_distance / num_rows
    avg_perplexity_ref = total_perplexity_ref / num_rows
    avg_perplexity_truth = total_perplexity_truth / num_rows
    avg_relevancy = total_relevancy / num_rows
    
    average_metrics = {
        "avg_similarity": avg_similarity,
        "avg_euclidean_distance": avg_euclidean_distance,
        "avg_perplexity_ref": avg_perplexity_ref,
        "avg_perplexity_truth": avg_perplexity_truth,
        "avg_relevancy": avg_relevancy
    }
    
    return average_metrics


file_path = "questions_answers.csv"
average_metrics = evaluate_from_csv(file_path)
    
print("Average Metrics:")
print(average_metrics)