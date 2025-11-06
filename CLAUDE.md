# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Retrieval-Augmented Generation (RAG) system for answering questions about course materials using semantic search and AI-powered responses. The system uses FastAPI for the backend, ChromaDB for vector storage, Anthropic's Claude for AI generation, and serves a web interface for user interaction.

## Architecture

### Core Components

- **FastAPI Application** (`backend/app.py`): Main web server with CORS middleware, static file serving, and API endpoints
- **RAG System** (`backend/rag_system.py`): Central orchestrator that coordinates document processing, vector search, and AI generation
- **Document Processor** (`backend/document_processor.py`): Handles parsing and chunking of course documents (PDF, DOCX, TXT)
- **Vector Store** (`backend/vector_store.py`): Manages ChromaDB for semantic search and course metadata storage
- **AI Generator** (`backend/ai_generator.py`): Interfaces with Anthropic's Claude API for response generation
- **Session Manager** (`backend/session_manager.py`): Manages conversation history and context
- **Search Tools** (`backend/search_tools.py`): Provides tool-based search capabilities for the AI

### Data Models

- **Course**: Contains course metadata, instructor info, and lessons
- **Lesson**: Individual lesson within a course with numbering and links
- **CourseChunk**: Text chunks for vector storage with course/lesson context

### Frontend

Simple HTML/CSS/JavaScript interface in `frontend/` directory that communicates with the backend API.

## Development Commands

### Setup and Installation

```bash
# Install dependencies
uv sync

# Set up environment variables (create .env file)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### Running the Application

```bash
# Quick start (recommended)
chmod +x run.sh
./run.sh

# Manual start
cd backend
uv run uvicorn app:app --reload --port 8000
```

The application will be available at:
- Web Interface: `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`

### Document Management

```bash
# Course documents should be placed in the docs/ directory
# Supported formats: PDF, DOCX, TXT
# Documents are automatically loaded on startup
```

## Configuration

Configuration is managed in `backend/config.py` with the following key settings:

- **ANTHROPIC_API_KEY**: Required for Claude AI integration
- **CHUNK_SIZE**: 800 characters for text chunking
- **CHUNK_OVERLAP**: 100 characters overlap between chunks
- **MAX_RESULTS**: 5 maximum search results
- **EMBEDDING_MODEL**: "all-MiniLM-L6-v2" for vector embeddings
- **CHROMA_PATH**: "./chroma_db" for vector database storage

## API Endpoints

- `POST /api/query`: Process user queries with RAG system
- `GET /api/courses`: Get course statistics and analytics
- Static files served from root path for frontend

## Important Notes

- The system automatically loads documents from the `docs/` directory on startup
- Each course title is used as a unique identifier - duplicate course titles are skipped
- Vector database persists in `backend/chroma_db/` directory
- Conversation sessions are maintained with configurable history length
- Tool-based search allows the AI to perform semantic searches on course content

## File Structure

```
project/
├── backend/          # Python FastAPI application
│   ├── app.py        # Main FastAPI server
│   ├── rag_system.py # Core RAG orchestration
│   ├── config.py     # Configuration settings
│   └── ...           # Other backend modules
├── frontend/         # Web interface
│   ├── index.html    # Main UI
│   ├── script.js     # Client-side logic
│   └── style.css     # Styling
├── docs/            # Course materials (PDF, DOCX, TXT)
├── run.sh           # Startup script
└── pyproject.toml   # Python dependencies
```
- 请确保使用uv来管理所有的依赖项