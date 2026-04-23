# Triển khai OpenAI API thực tế cho Reflexion Lab

Mục tiêu: Thay thế môi trường giả lập (mock_runtime) bằng việc gọi trực tiếp OpenAI API, đồng thời thu thập chính xác số lượng token và độ trễ (latency).

## User Review Required
- File `.env` sẽ được tạo sẵn, bạn cần điền `OPENAI_API_KEY` của bạn vào file đó.
- Vui lòng xem qua phần thay đổi file `agents.py` ở dưới để đảm bảo logic tính điểm token/latency phù hợp với mong đợi của bạn.

## Proposed Changes

### 1. Môi trường & Dependencies
- Thêm `openai` vào `requirements.txt`.
- Cài đặt các package cần thiết.
- Khởi tạo file `.env` với biến `OPENAI_API_KEY` rỗng (đã có `.env` trong `.gitignore`).

### 2. Prompts
#### [MODIFY] `src/reflexion_lab/prompts.py`
Hoàn thiện các System Prompts:
- **ACTOR_SYSTEM**: Hướng dẫn Agent phân tích Context để trả lời câu hỏi Multi-hop một cách ngắn gọn.
- **EVALUATOR_SYSTEM**: Hướng dẫn Giám khảo so sánh câu trả lời với Gold Answer và đưa ra `missing_evidence` (nếu có).
- **REFLECTOR_SYSTEM**: Hướng dẫn Agent rút ra `lesson` và `next_strategy` dựa trên lỗi sai của lần thử trước.

### 3. LLM Runtime
#### [NEW] `src/reflexion_lab/llm_runtime.py`
Tạo runtime mới để gọi OpenAI API:
- Định nghĩa hàm `actor_answer`: Gọi GPT-4o-mini (hoặc model do bạn chọn) để sinh câu trả lời.
- Định nghĩa hàm `evaluator`: Dùng `client.beta.chat.completions.parse(..., response_format=JudgeResult)` để LLM tự động trả về chuẩn Pydantic Schema.
- Định nghĩa hàm `reflector`: Tương tự, ép kiểu trả về là `ReflectionEntry`.
- Các hàm này sẽ trả về bộ 3 dữ liệu: `(kết_quả, tokens_used, latency_ms)` để tích hợp lên agents.py.

### 4. Cập nhật Agents
#### [MODIFY] `src/reflexion_lab/agents.py`
- Thay đổi `import` từ `mock_runtime` sang `llm_runtime`.
- Cập nhật hàm `.run()` để cộng dồn token và latency thực tế trả về từ các hàm API thay vì cộng số ngẫu nhiên (chỗ đang bị TO-DO).
- Lấy `FAILURE_MODE_BY_QID` từ mock vào agents hoặc tự suy luận cơ bản.

## Verification Plan
1. Chạy cấu hình LLM runtime với 1-2 câu hỏi đầu trong `hotpot_mini.json`.
2. Kiểm tra `outputs/sample_run/report.json` xem các token, answer và latency đã là đồ thật (real dynamic metrics) chưa.

