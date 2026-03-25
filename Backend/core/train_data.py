# ============================================================
# TRAINING MODULE - TRAINING SERVICE ONLY
# ============================================================
# This module handles PDF ingestion, text splitting, and
# embedding generation for legal documents.
# 
# TRAINING-ONLY DEPENDENCIES:
# - PyPDF2 (PDF reading)
# - langchain-core, langchain-text-splitters (text processing)
# - sentence-transformers (embeddings)
# 
# NOT USED BY CHAT SERVICE (main.py)
# Run only via training_service.py
# ============================================================

import logging
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# ============================================================
# TRAINING-ONLY IMPORTS
# ============================================================
from PyPDF2 import PdfReader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pymongo import UpdateOne  # type: ignore
from sentence_transformers import SentenceTransformer

from core.mongo_store import documents_collection, training_state_collection


BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
PDF_DIR = DATA_DIR / "pdfs"
CSV_PATH = DATA_DIR / "laws.csv"
LOG_DIR = DATA_DIR / "logs"
LOG_FILE = LOG_DIR / "training.log"


embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def setup_logger() -> logging.Logger:
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("lawgenie.training")
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    logger.propagate = False
    return logger


def build_pdf_fingerprint(pdf_file: Path) -> str:
    stat = pdf_file.stat()
    return f"{stat.st_size}:{stat.st_mtime_ns}"


def _safe_name(name: str) -> str:
    return name.replace(" ", "_").replace("/", "-")


def _normalized_pdf_name(name: str) -> str:
    normalized = _safe_name((name or "").strip())
    if not normalized.lower().endswith(".pdf"):
        normalized = f"{normalized}.pdf"
    return normalized.lower()


def build_source_map(logger: logging.Logger) -> Dict[str, Dict[str, str]]:
    source_map: Dict[str, Dict[str, str]] = {}

    if not CSV_PATH.exists():
        logger.warning("CSV not found at %s; source URL mapping disabled.", CSV_PATH)
        return source_map

    with open(CSV_PATH, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        expected_headers = ["PDF_Name", "Category", "Jurisdiction", "Subcategory", "PDF_Link"]
        missing_headers = [h for h in expected_headers if h not in (reader.fieldnames or [])]
        if missing_headers:
            raise ValueError(f"CSV missing required headers: {', '.join(missing_headers)}")

        for row in reader:
            name = (row.get("PDF_Name") or "").strip()
            pdf_url = (row.get("PDF_Link") or "").strip()
            category = (row.get("Category") or "").strip()
            jurisdiction = (row.get("Jurisdiction") or "").strip()
            subcategory = (row.get("Subcategory") or "").strip()

            if not name or not pdf_url:
                continue

            file_name = _normalized_pdf_name(name)
            source_map[file_name] = {
                "pdf_name": name,
                "pdf_link": pdf_url,
                "category": category,
                "jurisdiction": jurisdiction,
                "subcategory": subcategory,
            }

    logger.info("Loaded source mapping from CSV for %s entries", len(source_map))
    return source_map


def load_and_split_pdf(pdf_file: Path, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Document]:
    docs: List[Document] = []

    reader = PdfReader(str(pdf_file))
    full_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"

    if not full_text.strip():
        raise ValueError("No readable text found")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    chunks = splitter.split_text(full_text)

    for i, chunk in enumerate(chunks):
        docs.append(
            Document(
                page_content=chunk,
                metadata={
                    "source": str(pdf_file),
                    "source_name": pdf_file.name,
                    "chunk_index": i,
                },
            )
        )

    return docs


def embed_documents_local(docs: List[Document]):
    texts = [doc.page_content for doc in docs]
    vectors = embedding_model.encode(
        texts,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    return vectors


def _update_training_state(source_name: str, payload: Dict) -> None:
    now = datetime.utcnow()
    payload["updated_at"] = now

    training_state_collection.update_one(
        {"source_name": source_name},
        {
            "$set": payload,
            "$setOnInsert": {"created_at": now},
        },
        upsert=True,
    )


def _collect_pending_docs(source_name: str, fingerprint: str, docs: List[Document]) -> List[Tuple[int, Document]]:
    existing_indices = set(
        documents_collection.distinct(
            "chunk_index",
            {"source_name": source_name, "fingerprint": fingerprint},
        )
    )

    pending: List[Tuple[int, Document]] = []
    for i, doc in enumerate(docs):
        if i not in existing_indices:
            pending.append((i, doc))

    return pending


def _write_batch(
    source_name: str,
    pdf_link: str,
    source_meta: Dict[str, str],
    fingerprint: str,
    pairs: List[Tuple[int, Document]],
) -> int:
    if not pairs:
        return 0

    docs_only = [doc for _, doc in pairs]
    vectors = embed_documents_local(docs_only)
    if vectors.size == 0:
        return 0

    now = datetime.utcnow()
    operations = []
    for (i, doc), vector in zip(pairs, vectors):
        operations.append(
            UpdateOne(
                {"source_name": source_name, "chunk_index": i},
                {
                    "$set": {
                        "source": pdf_link,
                        "source_name": source_name,
                        "chunk_index": i,
                        "fingerprint": fingerprint,
                        "pdf_name": source_meta.get("pdf_name", ""),
                        "category": source_meta.get("category", ""),
                        "jurisdiction": source_meta.get("jurisdiction", ""),
                        "subcategory": source_meta.get("subcategory", ""),
                        "pdf_link": pdf_link,
                        "text": doc.page_content,
                        "embedding": vector.tolist(),
                        "updated_at": now,
                    },
                    "$setOnInsert": {
                        "created_at": now,
                    },
                },
                upsert=True,
            )
        )

    documents_collection.bulk_write(operations, ordered=False)
    return len(operations)


def train_file(
    pdf: Path,
    logger: logging.Logger,
    source_map: Dict[str, Dict[str, str]],
    batch_size: int = 64,
) -> Dict:
    source_name = pdf.name
    source_meta = source_map.get(source_name.lower(), {})
    source = source_meta.get("pdf_link", "")
    fingerprint = build_pdf_fingerprint(pdf)

    if not source:
        logger.info("%s skipped: not present in laws.csv mapping", source_name)
        return {"source_name": source_name, "status": "skipped", "chunks_written": 0, "total_chunks": 0}

    state = training_state_collection.find_one({"source_name": source_name}) or {}

    if state.get("fingerprint") and state.get("fingerprint") != fingerprint:
        deleted = documents_collection.delete_many({"source_name": source_name}).deleted_count
        logger.info("%s changed, deleted %s old chunks", source_name, deleted)

    _update_training_state(
        source_name,
        {
            "source": source,
            "fingerprint": fingerprint,
            "status": "in_progress",
            "started_at": datetime.utcnow(),
            "last_error": None,
        },
    )

    docs = load_and_split_pdf(pdf)
    total_chunks = len(docs)
    pending_pairs = _collect_pending_docs(source_name, fingerprint, docs)

    if total_chunks == 0:
        _update_training_state(
            source_name,
            {
                "source": source,
                "fingerprint": fingerprint,
                "status": "skipped",
                "total_chunks": 0,
                "processed_chunks": 0,
                "completed_at": datetime.utcnow(),
            },
        )
        logger.info("%s skipped: no chunks", source_name)
        return {"source_name": source_name, "status": "skipped", "chunks_written": 0, "total_chunks": 0}

    already_done = total_chunks - len(pending_pairs)
    logger.info(
        "%s total_chunks=%s already_done=%s pending=%s",
        source_name,
        total_chunks,
        already_done,
        len(pending_pairs),
    )

    _update_training_state(
        source_name,
        {
            "source": source,
            "fingerprint": fingerprint,
            "status": "in_progress",
            "total_chunks": total_chunks,
            "processed_chunks": already_done,
        },
    )

    written = 0
    if pending_pairs:
        for i in range(0, len(pending_pairs), batch_size):
            batch = pending_pairs[i : i + batch_size]
            inserted = _write_batch(source_name, source, source_meta, fingerprint, batch)
            written += inserted

            _update_training_state(
                source_name,
                {
                    "source": source,
                    "fingerprint": fingerprint,
                    "status": "in_progress",
                    "total_chunks": total_chunks,
                    "processed_chunks": already_done + written,
                },
            )
            logger.info(
                "%s batch_saved=%s progress=%s/%s",
                source_name,
                inserted,
                already_done + written,
                total_chunks,
            )

    final_processed = already_done + written
    final_status = "completed" if final_processed >= total_chunks else "in_progress"

    _update_training_state(
        source_name,
        {
            "source": source,
            "fingerprint": fingerprint,
            "status": final_status,
            "total_chunks": total_chunks,
            "processed_chunks": final_processed,
            "completed_at": datetime.utcnow() if final_status == "completed" else None,
        },
    )

    logger.info("%s done status=%s written=%s", source_name, final_status, written)
    return {
        "source_name": source_name,
        "status": final_status,
        "chunks_written": written,
        "total_chunks": total_chunks,
    }


def main() -> Dict:
    logger = setup_logger()
    logger.info("===== VECTOR TRAINING STARTED =====")
    source_map = build_source_map(logger)

    mapped_file_names = set(source_map.keys())
    pdf_files = sorted([pdf for pdf in PDF_DIR.glob("*.pdf") if pdf.name.lower() in mapped_file_names])
    if not pdf_files:
        logger.info("No mapped PDFs found in %s", PDF_DIR)
        return {
            "status": "success",
            "message": "No mapped PDFs found.",
            "files_total": 0,
            "files_processed": 0,
            "files_failed": 0,
            "chunks_added": 0,
        }

    summary = {
        "status": "success",
        "message": "Training completed.",
        "files_total": len(pdf_files),
        "files_processed": 0,
        "files_failed": 0,
        "chunks_added": 0,
        "results": [],
    }

    try:
        for pdf in pdf_files:
            result = train_file(pdf, logger=logger, source_map=source_map)
            summary["results"].append(result)
            summary["files_processed"] += 1
            summary["chunks_added"] += int(result.get("chunks_written", 0))

    except KeyboardInterrupt:
        summary["status"] = "interrupted"
        summary["message"] = "Training interrupted. Resume by running training again."
        logger.warning("Training interrupted by user; progress saved in MongoDB.")
        return summary

    except Exception as e:
        summary["status"] = "error"
        summary["message"] = str(e)
        summary["files_failed"] += 1
        logger.exception("Fatal training error: %s", e)
        return summary

    total_chunks = documents_collection.count_documents({})
    logger.info("Training completed | files=%s chunks_added=%s total_chunks=%s", summary["files_processed"], summary["chunks_added"], total_chunks)
    return summary


if __name__ == "__main__":
    result = main()
    print(result)
