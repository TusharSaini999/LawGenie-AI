# Requirements Files

This directory contains separated and combined requirements files for the LawGenie AI Backend.

## Files Overview

### `requirements.txt` (Default - Recommended for Most Cases)
**Use this for development or when both services might run together.**

- Includes **ALL** dependencies for both chat and training services
- Easiest to manage - single file
- Suitable for local development where you might run both services

```bash
pip install -r requirements.txt
```

---

### `requirements-chat.txt` (Chat Service Only - Production Recommended)
**Use this for production deployment of the chat service.**

- **Lightweight** - Only dependencies needed by chat service
- Does NOT include: PyPDF2, langchain-core, langchain-text-splitters
- Includes: FastAPI, MongoDB, JWT, Groq LLM client
- Chat retrieval uses MongoDB Atlas Search only, so no local embedding model is required
- **Production deployments should use this** since training is optional

```bash
pip install -r requirements-chat.txt
```

---

### `requirements-training.txt` (Training Service Only)
**Use this if running the training service separately.**

- Includes **ALL** training-specific dependencies
- Suitable for a dedicated training machine/container
- Runs independently of the chat service

```bash
pip install -r requirements-training.txt
```

---

### `requirements-all.txt` (Complete)
**Alias for requirements.txt - includes everything.**

- Same as `requirements.txt`
- Use if you want explicit clarity that you're installing all dependencies

```bash
pip install -r requirements-all.txt
```

---

## Dependency Breakdown

### Chat Service Only (requirements-chat.txt)
```
FastAPI
Uvicorn
Pydantic
MongoDB (PyMongo)
JWT (PyJWT)
Groq API client
```

**NOT included:**
- ❌ PyPDF2 (PDF reading)
- ❌ langchain-core (text splitting)
- ❌ langchain-text-splitters
- ❌ numpy, sentence-transformers, torch, transformers

### Training Service Only (requirements-training.txt)
```
FastAPI
Uvicorn
Pydantic
MongoDB (PyMongo)
JWT (PyJWT)
Groq API client
PyPDF2 (PDF reading)
langchain-core (text document handling)
langchain-text-splitters (chunk splitting)
numpy
sentence-transformers (for document embeddings)
torch, transformers
```

### Shared Dependencies
These libraries are used by **training only**:
- `sentence-transformers` - Document embedding generation
- `torch`, `transformers` - Required by sentence-transformers

---

## Deployment Guide

### Production: Chat Service Only
```bash
# Most efficient production deployment
pip install -r requirements-chat.txt

# Start chat service
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Production: Training Service
```bash
# If running training separately
pip install -r requirements-training.txt

# Start training service
uvicorn training_service:training_app --host 0.0.0.0 --port 8001
```

### Development: Both Services
```bash
# Development with both services
pip install -r requirements.txt

# Terminal 1: Chat service
uvicorn main:app --reload

# Terminal 2: Training service
uvicorn training_service:training_app --port 8001 --reload
```

---

## Dependency Size Notes

| File | Size | Use Case |
|------|------|----------|
| `requirements-chat.txt` | ~Smaller | Production chat deployment |
| `requirements-training.txt` | ~Larger | Training service (resource-intensive) |
| `requirements.txt` | ~Largest | Development, both services |

Training libraries like `torch` and `langchain` are significantly larger, so using `requirements-chat.txt` for production will reduce deployment size.

---

## Checking Which Service Uses What

Look for comments in the code marking training-only modules:

- `core/train_data.py` - TRAINING ONLY (marked with comments)
- `routes/train_route.py` - TRAINING ONLY (marked with comments)
- `training_service.py` - TRAINING SERVICE ENDPOINT (marked with comments)
- `core/query_engine.py` - CHAT SERVICE (Atlas Search only)
- `main.py` - CHAT SERVICE ONLY (training route removed)
