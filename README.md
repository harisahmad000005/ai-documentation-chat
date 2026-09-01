# AI Documentation Chat

A Retrieval-Augmented Generation (RAG) application for uploading documentation, processing it into searchable vector embeddings, and interacting with it through AI-powered conversations.

Built with FastAPI, PostgreSQL, pgvector, LangChain, and Ollama, with user authentication and persistent chat history.

## Features

- Document upload and processing
- Semantic search using vector embeddings
- AI-powered question answering using RAG
- Multiple conversations per user
- Persistent chat and message history
- JWT-based authentication
- Argon2 password hashing
- User activation workflow
- User-specific document isolation
- Local LLM inference through Ollama
- PostgreSQL with pgvector
- Docker-friendly development environment
- SQLAdmin interface for administration
- Automated tests
- Database migrations with Alembic

---

## Architecture

The application follows a layered architecture that separates authentication, document processing, retrieval, and AI generation.

```text
                    ┌─────────────────────┐
                    │       FastAPI        │
                    │      REST API        │
                    └──────────┬──────────┘
                               │
             ┌─────────────────┼─────────────────┐
             │                 │                 │
             ▼                 ▼                 ▼
       Authentication      Documents           Chats
             │                 │                 │
             ▼                 ▼                 ▼
        JWT / User      Extraction/Chunking   Messages
                               │
                               ▼
                          Embeddings
                               │
                               ▼
                     PostgreSQL + pgvector
                               │
                               ▼
                      Semantic Retrieval
                               │
                               ▼
                        RAG Pipeline
                               │
                               ▼
                            Ollama
                               │
                               ▼
                      Generated Answer
```

---

## Technology Stack

| Component | Technology |
|---|---|
| API | FastAPI |
| Language | Python |
| Database | PostgreSQL |
| Vector Database | pgvector |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| RAG | LangChain |
| LLM | Ollama |
| Chat Model | Llama 3.2 |
| Embedding Model | nomic-embed-text |
| Embedding Dimensions | 768 |
| Authentication | JWT |
| Password Hashing | Argon2id |
| Administration | SQLAdmin |
| Containerization | Docker |

---

## RAG Pipeline

The core document question-answering workflow:

```text
Document Upload
      │
      ▼
Document Extraction
      │
      ▼
Text Chunking
      │
      ▼
Generate Embeddings
      │
      ▼
Store Chunks and Vectors
      │
      ▼
User Question
      │
      ▼
Generate Query Embedding
      │
      ▼
Vector Similarity Search
      │
      ▼
Retrieve Relevant Chunks
      │
      ▼
Build RAG Context
      │
      ▼
LLM Generation
      │
      ▼
AI Answer
```

The application uses `nomic-embed-text` to generate 768-dimensional embeddings, stored in PostgreSQL via pgvector.

---

## Authentication

Authentication is based on JWT access tokens. Passwords are never stored in plaintext; they are hashed using Argon2id before being persisted.

### User Activation

New users are inactive by default:

```text
Registration
     │
     ▼
is_active = false
     │
     ▼
Admin reviews account
     │
     ▼
Admin activates user
     │
     ▼
is_active = true
     │
     ▼
User can log in
```

An inactive user cannot obtain an access token. The application also verifies user active status on every authenticated request, allowing an administrator to deactivate an account even after a token has been issued.

---

## Multi-User Data Isolation

Each user owns their documents and conversations.

```text
User
 ├── Documents
 │    └── Document Chunks
 │
 └── Chats
      └── Chat Messages
```

Application queries are scoped to the authenticated user's ID, for example:

```python
select(Chat).where(
    Chat.id == chat_id,
    Chat.user_id == current_user.id,
)
```

This prevents one authenticated user from accessing another user's data. The same isolation principle applies to document and vector retrieval.

---

## Chat Architecture

A user can maintain multiple independent conversations.

```text
User
 │
 ├── Chat 1
 │    ├── User Message
 │    ├── Assistant Message
 │    ├── User Message
 │    └── Assistant Message
 │
 ├── Chat 2
 │    ├── User Message
 │    └── Assistant Message
 │
 └── Chat 3
      ├── User Message
      └── Assistant Message
```

Chat messages are stored as individual database records rather than as a single JSON blob per conversation. This design simplifies:

- Retrieving conversation history
- Paginating messages
- Deleting conversations
- Extending messages with metadata
- Adding citations and retrieved sources in the future

---

## Project Structure

```text
ai-documentation-chat/
│
├── app/
│   ├── admin/
│   │   ├── auth.py
│   │   └── views/
│   │
│   ├── api/
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── constants.py
│   │   └── security.py
│   │
│   ├── database/
│   │   ├── base.py
│   │   └── session.py
│   │
│   ├── models/
│   │   ├── chat.py
│   │   ├── chat_message.py
│   │   ├── document.py
│   │   ├── document_chunk.py
│   │   ├── user.py
│   │   └── mixins.py
│   │
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── chat.py
│   │   └── ...
│   │
│   ├── services/
│   │   ├── authentication.py
│   │   ├── chat.py
│   │   ├── embeddings.py
│   │   └── ...
│   │
│   └── main.py
│
├── alembic/
│   └── versions/
│
├── envs/
│   └── .env
│
├── tests/
│
├── docker-compose.yml
├── Dockerfile
├── alembic.ini
├── requirements.txt
└── README.md
```

---

## Requirements

- Python 3.11+
- PostgreSQL
- pgvector
- Ollama
- Git
- Docker / Docker Compose (optional)

---

## Environment Configuration

Create an environment file:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ai_documentation_chat

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_CHAT_MODEL=llama3.2
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

ADMIN_USERNAME=admin
ADMIN_PASSWORD=change-me
ADMIN_SECRET_KEY=change-this-secret

JWT_SECRET_KEY=change-this-to-a-long-random-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Do not commit the `.env` file or production secrets to source control. Generate a strong, unique JWT secret for production rather than using the example value above.

---

## Running Ollama

Pull the required models:

```bash
ollama pull llama3.2
ollama pull nomic-embed-text
```

Verify Ollama is running:

```bash
ollama list
```

---

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd ai-documentation-chat
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it.

**Windows**

```bash
.venv\Scripts\activate
```

**Linux / macOS**

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Database Setup

Run the database migrations:

```bash
alembic upgrade head
```

This creates the required schema, including:

- Users
- Documents
- Document chunks
- Chats
- Chat messages

---

## Running the Application

Start the FastAPI application:

```bash
uvicorn app.main:app --reload
```

The API is available at `http://localhost:8000`.

Interactive API documentation: `http://localhost:8000/docs`
Alternative documentation: `http://localhost:8000/redoc`

---

## Docker

The project can also be run using Docker Compose:

```bash
docker compose up --build
```

To run in the background:

```bash
docker compose up --build -d
```

Stop the services:

```bash
docker compose down
```

---

## Database Migrations

Create a new migration after changing SQLAlchemy models:

```bash
alembic revision --autogenerate -m "describe your change"
```

Review the generated migration before applying it. Apply migrations:

```bash
alembic upgrade head
```

Roll back the latest migration:

```bash
alembic downgrade -1
```

---

## API Overview

The API is organized around authenticated users, documents, and conversations.

**Authentication**

```text
POST /auth/register
POST /auth/login
GET  /auth/me
```

**Documents**

```text
POST   /documents
GET    /documents
GET    /documents/{document_id}
DELETE /documents/{document_id}
```

**Chats**

```text
POST   /chats
GET    /chats
GET    /chats/{chat_id}
DELETE /chats/{chat_id}
```

**Messages**

```text
POST /chats/{chat_id}/messages
GET  /chats/{chat_id}/messages
```

Exact routes may vary as the API layer evolves.

---

## Security Considerations

- Passwords are hashed using Argon2id.
- JWT signing uses a dedicated secret.
- SQLAdmin authentication uses a separate secret.
- Inactive users cannot log in.
- Authenticated requests resolve the current user from the JWT.
- User-owned resources are scoped to the authenticated user's ID.
- Secrets are provided through environment variables.
- Password hashes are never returned in API responses.
- JWTs contain only the information required for authentication.

---

## Future Improvements

- Refresh token authentication
- Password reset functionality
- Email verification
- Role-based access control
- Streaming LLM responses
- Automatically generated conversation titles
- Source citations for retrieved chunks
- Retrieval and response metadata
- Hybrid keyword and vector search
- Reranking of retrieved documents
- Background document processing
- Document versioning
- File storage using S3-compatible object storage
- Rate limiting
- API usage tracking
- Observability and structured logging
- Production deployment with Docker
- CI/CD pipeline

---

## Development

Run the test suite:

```bash
pytest
```

Run tests before creating a pull request or pushing significant changes.

---

## Design Goals

1. **Security first** — authentication, authorization, and tenant isolation are enforced at the application layer.
2. **Separation of concerns** — API, database, services, retrieval, and LLM logic remain independently maintainable.
3. **Persistent state** — documents and conversations are stored in the database rather than relying on in-memory state.
4. **Scalability** — expensive document processing and AI workloads can be moved to background workers as the application grows.
5. **Extensibility** — the architecture supports adding new models, vector stores, storage providers, and authentication methods without major rewrites.

---

## License

This project is currently private and under active development. Add the appropriate license when the repository is made public.