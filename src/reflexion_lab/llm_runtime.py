from __future__ import annotations
import os
import time
from dotenv import load_dotenv
from typing import Tuple
from openai import OpenAI

from .schemas import QAExample, JudgeResult, ReflectionEntry
from .prompts import ACTOR_SYSTEM, EVALUATOR_SYSTEM, REFLECTOR_SYSTEM

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL_NAME = "gpt-4o-mini"

def actor_answer(example: QAExample, attempt_id: int, agent_type: str, reflection_memory: list[str]) -> Tuple[str, int, int]:
    start_time = time.time()
    
    context_str = "\n".join([f"[{c.title}] {c.text}" for c in example.context])
    user_msg = f"CONTEXT:\n{context_str}\n\nQUESTION:\n{example.question}\n"
    
    if reflection_memory and agent_type == "reflexion":
        reflections_str = "\n".join([f"- {r}" for r in reflection_memory])
        user_msg += f"\nYOUR PAST LESSONS:\n{reflections_str}\nEnsure you strictly follow your past strategies and do not repeat mistakes!"

    messages = [
        {"role": "system", "content": ACTOR_SYSTEM},
        {"role": "user", "content": user_msg}
    ]
    
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=0.0
    )
    
    answer = response.choices[0].message.content.strip() if response.choices[0].message.content else ""
    tokens = response.usage.total_tokens if response.usage else 0
    latency = int((time.time() - start_time) * 1000)
    
    return answer, tokens, latency

def evaluator(example: QAExample, answer: str) -> Tuple[JudgeResult, int, int]:
    start_time = time.time()
    
    user_msg = (
        f"QUESTION: {example.question}\n"
        f"GOLD ANSWER: {example.gold_answer}\n"
        f"STUDENT ANSWER: {answer}\n"
        f"Please judge the student's answer."
    )
    
    messages = [
        {"role": "system", "content": EVALUATOR_SYSTEM},
        {"role": "user", "content": user_msg}
    ]
    
    response = client.beta.chat.completions.parse(
        model=MODEL_NAME,
        messages=messages,
        response_format=JudgeResult,
        temperature=0.0
    )
    
    result = response.choices[0].message.parsed
    if not result:
        # Fallback in case parsing somehow fails
        result = JudgeResult(score=0, reason="Failed to parse evaluator response.")
        
    tokens = response.usage.total_tokens if response.usage else 0
    latency = int((time.time() - start_time) * 1000)
    
    return result, tokens, latency

def reflector(example: QAExample, attempt_id: int, judge: JudgeResult) -> Tuple[ReflectionEntry, int, int]:
    start_time = time.time()
    
    context_str = "\n".join([f"[{c.title}] {c.text}" for c in example.context])
    user_msg = (
        f"CONTEXT:\n{context_str}\n\n"
        f"QUESTION: {example.question}\n"
        f"FEEDBACK FROM JUDGE:\nReason: {judge.reason}\n"
        f"Missing Evidence: {', '.join(judge.missing_evidence)}\n"
        f"Please provide an insightful reflection to help the actor do better."
    )
    
    messages = [
        {"role": "system", "content": REFLECTOR_SYSTEM},
        {"role": "user", "content": user_msg}
    ]
    
    response = client.beta.chat.completions.parse(
        model=MODEL_NAME,
        messages=messages,
        response_format=ReflectionEntry,
        temperature=0.0
    )
    
    entry = response.choices[0].message.parsed
    if not entry:
        entry = ReflectionEntry(
            attempt_id=attempt_id,
            failure_reason="Could not generate reflection.",
            lesson="Try again more carefully.",
            next_strategy="Re-read the context."
        )
    else:
        entry.attempt_id = attempt_id
        
    tokens = response.usage.total_tokens if response.usage else 0
    latency = int((time.time() - start_time) * 1000)
    
    return entry, tokens, latency
