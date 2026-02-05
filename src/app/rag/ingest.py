import argparse
import os
from pathlib import Path
from typing import List

import pdfplumber
from rich.console import Console
from rich.progress import track

from app.rag.vector_store import DocumentChunk
from app.rag.retriever import Retriever
from app.utils.text import clean_text, chunk_text

console = Console()


def extract_pdf_chunks(pdf_path: Path) -> List[DocumentChunk]:
    chunks: List[DocumentChunk] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            text = clean_text(text)
            for idx, chunk in enumerate(chunk_text(text)):
                chunks.append(
                    DocumentChunk(
                        text=chunk,
                        document=pdf_path.name,
                        section=f"page-{page_num}-chunk-{idx}",
                        page=page_num,
                    )
                )
    return chunks


def ingest(data_dir: Path):
    retriever = Retriever()
    pdfs = list(data_dir.glob("*.pdf"))
    if not pdfs:
        console.print("[yellow]No PDFs found in data/. Place manuals before ingesting.[/yellow]")
        return
    total_chunks = 0
    for pdf_path in track(pdfs, description="Ingesting PDFs"):
        chunks = extract_pdf_chunks(pdf_path)
        retriever.add_documents(chunks)
        total_chunks += len(chunks)
    console.print(f"[green]Ingestion complete.[/green] Added {total_chunks} chunks.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest PDFs into FAISS store.")
    parser.add_argument(
        "--data_dir",
        type=Path,
        default=Path("data"),
        help="Directory containing PDFs",
    )
    args = parser.parse_args()
    os.makedirs(args.data_dir, exist_ok=True)
    ingest(args.data_dir)

