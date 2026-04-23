from datasets import load_dataset
import json

# Load dataset
ds = load_dataset("hotpotqa/hotpot_qa", name="distractor", split="train")

# Lấy 100 dòng đầu
first_100 = ds.select(range(100))

# Lưu ra JSON
with open("hotpot_qa_first_100.json", "w", encoding="utf-8") as f:
    json.dump(first_100.to_list(), f, ensure_ascii=False, indent=2)

print("Đã lưu vào file hotpot_qa_first_100.json")