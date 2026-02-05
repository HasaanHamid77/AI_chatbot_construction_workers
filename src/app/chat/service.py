from __future__ import annotations

from typing import List, Tuple

from app.chat.model_client import ModelClient
from app.rag.retriever import Retriever, sanitize_context
from app.safety import policies
from app.safety.crisis import CRISIS_TEMPLATE, detect_crisis
from app.safety.playbooks import wellbeing_response
from app.schemas import ChatRequest, ChatResponse, Message, SourceRef


class ChatService:
    def __init__(self):
        self.model = ModelClient()
        self.retriever = Retriever()

    def handle_chat(self, req: ChatRequest) -> ChatResponse:
        user_text = " ".join([m.content for m in req.messages if m.role == "user"])
        crisis_signal = detect_crisis(user_text)
        if crisis_signal.triggered:
            reply = CRISIS_TEMPLATE.format(disclosure=policies.AI_DISCLOSURE)
            return ChatResponse(
                reply=reply, citations=[], safety_notes="crisis_escalation_triggered"
            )

        mode = req.mode
        if mode == "wellbeing":
            return ChatResponse(
                reply=wellbeing_response(),
                citations=[],
                safety_notes="wellbeing_playbook",
            )

        # Default: try technical with RAG; fallback to wellbeing playbook if no context.
        citations, context_block = self._retrieve_context(user_text)
        if not context_block:
            return ChatResponse(
                reply=f"{policies.AI_DISCLOSURE} {policies.TECH_BOUNDARY} {policies.REFUSAL_NO_CONTEXT}",
                citations=[],
                safety_notes="no_context",
            )

        prompt = self._build_prompt(user_text, context_block, citations)
        model_reply = self.model.generate(prompt)
        return ChatResponse(reply=model_reply, citations=citations)

    def _retrieve_context(self, query: str) -> Tuple[List[SourceRef], str]:
        results = self.retriever.retrieve(query, k=4)
        if not results:
            return [], ""
        chunks = [r[0] for r in results]
        citations = [
            SourceRef(document=c.document, section=c.section, page=c.page)
            for c in chunks
        ]
        context_block = sanitize_context(chunks)
        return citations, context_block

    def _build_prompt(
        self, query: str, context_block: str, citations: List[SourceRef]
    ) -> str:
        citation_lines = [
            f"- {c.document} ({c.section or 'unknown section'} p.{c.page or '?'})"
            for c in citations
        ]
        return "\n".join(
            [
                policies.AI_DISCLOSURE,
                policies.TECH_BOUNDARY,
                policies.PROMPT_INJECTION_WARNING,
                "Use ONLY the context below. If insufficient, say you lack information and suggest supervisor review.",
                "Context:",
                context_block,
                "Citations:",
                "\n".join(citation_lines),
                "User question:",
                query,
                "Answer with concise steps, cite sources by name + section/page, and do not invent information.",
            ]
        )

