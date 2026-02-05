from fastapi import FastAPI, HTTPException

from app.chat.service import ChatService
from app.gpu.service import GPUService
from app.schemas import ChatRequest, ChatResponse

app = FastAPI(title="Construction Safety Support Assistant")
chat_service = ChatService()
gpu_service: GPUService | None = None

# Lazy init GPU service so app can start without RunPod creds for non-GPU flows.
def get_gpu_service() -> GPUService:
    global gpu_service
    if gpu_service is None:
        try:
            gpu_service = GPUService()
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
    return gpu_service


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/v1/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """
    Core chat endpoint.
    - Detects crisis signals and escalates.
    - Wellbeing mode: structured coping playbooks.
    - Technical mode: RAG with citations; refuses to guess.
    """
    return chat_service.handle_chat(req)


@app.post("/gpu/start")
def gpu_start():
    """
    Start the RunPod GPU pod (Option A: control existing pod).
    Also schedules an auto-stop after configured idle timeout.
    """
    svc = get_gpu_service()
    return svc.start()


@app.post("/gpu/stop")
def gpu_stop():
    """
    Stop the RunPod GPU pod and cancel any pending auto-stop timer.
    """
    svc = get_gpu_service()
    return svc.stop()


@app.get("/gpu/status")
def gpu_status():
    """
    Get current RunPod pod status.
    """
    svc = get_gpu_service()
    return svc.status()

