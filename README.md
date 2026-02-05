# Construction Worker Safety Assistant (Prototype)

Research-grade prototype of a safety-first conversational assistant for construction workers. The system provides two bounded capabilities:
1) **Mental wellbeing support** (non-clinical, non-diagnostic).
2) **Construction technical support** grounded in retrieved documents (RAG).

## Principles
- Always disclose it is an AI support tool, not a therapist or clinician.
- Never provide diagnosis, treatment, or medical advice.
- Escalate empathetically on crisis signals (self-harm, violence, abuse).
- Technical answers must be grounded in retrieved documents with citations; refuse to guess.
- Reject unsafe requests and recommend supervisor/safety officer escalation.

## Tech Stack (intended)
- Python 3.10+
- FastAPI app layer
- vLLM serving an open-source instruct model (e.g., Qwen2.5 3B Instruct)
- BGE-family embeddings
- FAISS (default) or Chroma vector store
- SQLite or Postgres for logs (MVP uses SQLite)
- Docker (optional, not yet provided)

## Layout
- `src/app/main.py` — FastAPI entrypoint and routes.
- `src/app/config.py` — configuration/env handling.
- `src/app/schemas.py` — request/response models.
- `src/app/safety/` — guardrails, playbooks, crisis handling.
- `src/app/rag/` — ingestion, retrieval, and context assembly.
- `src/app/chat/` — orchestration of generation + safety layers.
- `data/` — place PDFs/manuals to ingest.
- `storage/` — vector DB + logs (created at runtime).

## Quickstart (local, dev)
1) Create venv and install:
   ```bash
   python -m venv .venv
   source .venv/Scripts/activate  # Windows PowerShell: .venv\\Scripts\\Activate.ps1
   pip install -r requirements.txt
   ```
2) Ingest docs (place PDFs in `data/` first):
   ```bash
   python src/app/rag/ingest.py
   ```
   - Embeddings: defaults to `BAAI/bge-small-en-v1.5`.
   - Vector DB: FAISS stored under `storage/faiss.index`.
3) Run API:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
4) Test health:
   ```bash
   curl http://localhost:8000/health
   ```
5) Sample chat:
   ```bash
   curl -X POST http://localhost:8000/v1/chat \
     -H "Content-Type: application/json" \
     -d "{\"messages\":[{\"role\":\"user\",\"content\":\"How do I inspect scaffold planks?\"}]}"
   ```

## Docker
### API (CPU) container
Build and run:
```bash
docker build -t cw-assistant -f Dockerfile .
docker run -p 8000:8000 --env-file .env cw-assistant
```

### GPU (vLLM) container
Build (or use upstream vllm/vllm-openai image):
```bash
docker build -t cw-vllm -f Dockerfile.gpu .
```
Run with NVIDIA runtime (example):
```bash
docker run --gpus all -p 8001:8001 \
  -e MODEL=Qwen2.5-3B-Instruct \
  -e MODEL_NAME=Qwen2.5-3B-Instruct \
  cw-vllm
```
Then set `CW_MODEL_SERVER_URL=http://<gpu-host>:8001/v1/chat/completions`.

## RunPod GPU control (Option A: best)
- Set env in `.env` for the CPU API:
  - `CW_RUNPOD_API_KEY=<your key>`
  - `CW_RUNPOD_POD_ID=<existing pod id>`
  - `CW_RUNPOD_IDLE_TIMEOUT_MINUTES=30` (auto-stop window)
- Endpoints:
  - `POST /gpu/start` — starts pod, schedules auto-stop after idle timeout.
  - `POST /gpu/stop` — stops pod immediately.
  - `GET /gpu/status` — returns RunPod pod status.
- Frontend flow: user clicks “Activate GPU” → call `/gpu/start`; wait for pod to become READY; chat uses `CW_MODEL_SERVER_URL` pointed to the pod’s vLLM endpoint. Call `/gpu/stop` (or let auto-stop) when done.

## Safety behaviors (high level)
- Crisis detection: checks for self-harm/violence/abuse keywords and responds with empathy + escalation guidance only.
- Mental wellbeing mode: structured playbooks (grounding, problem-solving, conflict scripts) with conservative language.
- Technical mode: runs retrieval, applies prompt-injection filters on retrieved text, cites documents (name + section/page).
- If retrieval is weak/empty: politely refuse to answer and recommend talking to a supervisor or checking official manuals.

## Notes / Next steps
- vLLM client is stubbed; wire to your deployment (HTTP server) in `chat/model_client.py`.
- Add Dockerfile and CI as needed.
- Expand crisis lexicon and add tests.
- Consider adding reranking and E2E logging to Postgres.

This code is intentionally explicit and conservative to aid safety review.

