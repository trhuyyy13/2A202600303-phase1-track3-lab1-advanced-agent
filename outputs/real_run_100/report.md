# Lab 16 Benchmark Report

## Metadata
- Dataset: hotpot_qa_first_100.json
- Mode: llm
- Records: 200
- Agents: react, reflexion

## Summary
| Metric | ReAct | Reflexion | Delta |
|---|---:|---:|---:|
| EM | 0.84 | 0.91 | 0.07 |
| Avg attempts | 1 | 1.28 | 0.28 |
| Avg token estimate | 2017.83 | 3145.31 | 1127.48 |
| Avg latency (ms) | 2534.5 | 4136.58 | 1602.08 |

## Failure modes
```json
{
  "react": {
    "none": 84,
    "wrong_final_answer": 16
  },
  "reflexion": {
    "none": 91,
    "wrong_final_answer": 9
  }
}
```

## Extensions implemented
- structured_evaluator
- reflection_memory
- benchmark_report_json
- mock_mode_for_autograding

## Discussion
Reflexion helps when the first attempt stops after the first hop or drifts to a wrong second-hop entity. The tradeoff is higher attempts, token cost, and latency. In a real report, students should explain when the reflection memory was useful, which failure modes remained, and whether evaluator quality limited gains.
