from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Iterable
from .schemas import QAExample, RunRecord

def normalize_answer(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text

def load_dataset(path: str | Path) -> list[QAExample]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    examples = []
    for item in raw:
        # If it's already in the QAExample format (e.g. mock mini dataset)
        if "qid" in item:
            examples.append(QAExample.model_validate(item))
        else:
            # It's raw HotpotQA format
            context_chunks = []
            for i, title in enumerate(item["context"]["title"]):
                text = " ".join(item["context"]["sentences"][i])
                context_chunks.append({"title": title, "text": text})
                
            example = QAExample(
                qid=item["id"],
                difficulty=item["level"],
                question=item["question"],
                gold_answer=item["answer"],
                context=context_chunks
            )
            examples.append(example)
    return examples

def save_jsonl(path: str | Path, records: Iterable[RunRecord]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(record.model_dump_json() + "\n")
